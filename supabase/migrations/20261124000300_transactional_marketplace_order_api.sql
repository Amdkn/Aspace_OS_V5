-- A'Space Marketplace Day 2 — transactional order operations
BEGIN;
CREATE OR REPLACE FUNCTION api.create_marketplace_order(
  p_actor_user_id uuid,
  p_buyer_organization_id uuid,
  p_listing_id uuid,
  p_idempotency_key text
)
RETURNS commerce.orders
LANGUAGE plpgsql SECURITY DEFINER
SET search_path = pg_catalog, identity, catalog, commerce, api, auth
AS $function$
DECLARE
  v_listing catalog.listings%ROWTYPE;
  v_order commerce.orders%ROWTYPE;
  v_created boolean := false;
BEGIN
  IF p_actor_user_id IS NULL OR p_buyer_organization_id IS NULL OR p_listing_id IS NULL
     OR p_idempotency_key IS NULL OR length(p_idempotency_key) NOT BETWEEN 8 AND 200 THEN
    RAISE EXCEPTION 'Invalid order request';
  END IF;
  PERFORM 1 FROM identity.organization_memberships m
  WHERE m.organization_id = p_buyer_organization_id AND m.user_id = p_actor_user_id
    AND m.membership_status = 'ACTIVE';
  IF NOT FOUND THEN RAISE EXCEPTION 'Buyer organization membership required'; END IF;
  PERFORM 1 FROM identity.role_bindings rb
  WHERE rb.organization_id = p_buyer_organization_id AND rb.subject_user_id = p_actor_user_id
    AND rb.binding_status = 'ACTIVE' AND rb.starts_at <= now()
    AND (rb.expires_at IS NULL OR rb.expires_at > now())
    AND rb.role_code IN ('S0_SOVEREIGN','B1_CEO','A3_PICARD','B2_MANAGER');
  IF NOT FOUND THEN RAISE EXCEPTION 'Order placement role required'; END IF;
  SELECT * INTO v_listing FROM catalog.listings l WHERE l.id = p_listing_id FOR SHARE;
  IF NOT FOUND OR v_listing.listing_status <> 'PUBLISHED' THEN RAISE EXCEPTION 'Published listing not found'; END IF;
  IF v_listing.owner_organization_id = p_buyer_organization_id THEN RAISE EXCEPTION 'Self-purchase is not allowed'; END IF;
  INSERT INTO commerce.orders (
    order_number,idempotency_key,buyer_organization_id,seller_organization_id,
    listing_id,listing_version,capability_id,capability_version_id,
    listing_title_snapshot,price_amount_snapshot,currency_snapshot,
    acceptance_criteria_snapshot,order_status,created_by_user_id
  ) VALUES (
    'ORD-' || upper(substr(replace(gen_random_uuid()::text,'-',''),1,12)),
    p_idempotency_key,p_buyer_organization_id,v_listing.owner_organization_id,
    v_listing.id,v_listing.version,v_listing.capability_id,v_listing.capability_version_id,
    v_listing.title,v_listing.price_amount,v_listing.currency,
    v_listing.acceptance_criteria,'PLACED',p_actor_user_id
  )
  ON CONFLICT (buyer_organization_id,idempotency_key) DO NOTHING
  RETURNING * INTO v_order;
  IF FOUND THEN
    v_created := true;
  ELSE
    SELECT * INTO v_order FROM commerce.orders
    WHERE buyer_organization_id = p_buyer_organization_id AND idempotency_key = p_idempotency_key;
    IF v_order.listing_id <> p_listing_id THEN RAISE EXCEPTION 'Idempotency key already belongs to another listing'; END IF;
  END IF;
  IF v_created THEN
    INSERT INTO commerce.order_events (
      order_id,sequence_number,from_status,to_status,actor_type,
      actor_user_id,actor_organization_id,reason
    ) VALUES (v_order.id,1,NULL,'PLACED','HUMAN',p_actor_user_id,p_buyer_organization_id,'Order placed');
  END IF;
  RETURN v_order;
END
$function$;

CREATE OR REPLACE FUNCTION api.transition_marketplace_order(
  p_actor_user_id uuid,
  p_order_id uuid,
  p_actor_organization_id uuid,
  p_target_status text,
  p_reason text
)
RETURNS commerce.orders
LANGUAGE plpgsql SECURITY DEFINER
SET search_path = pg_catalog, identity, catalog, commerce, api, auth
AS $function$
DECLARE
  v_order commerce.orders%ROWTYPE;
  v_sequence integer;
  v_is_buyer boolean;
  v_is_seller boolean;
BEGIN
  IF p_actor_user_id IS NULL OR p_order_id IS NULL OR p_actor_organization_id IS NULL
     OR p_reason IS NULL OR length(btrim(p_reason)) = 0 THEN
    RAISE EXCEPTION 'Invalid order transition request';
  END IF;
  SELECT * INTO v_order FROM commerce.orders WHERE id = p_order_id FOR UPDATE;
  IF NOT FOUND THEN RAISE EXCEPTION 'Order not found'; END IF;
  v_is_buyer := p_actor_organization_id = v_order.buyer_organization_id;
  v_is_seller := p_actor_organization_id = v_order.seller_organization_id;
  IF NOT (v_is_buyer OR v_is_seller) THEN RAISE EXCEPTION 'Order party required'; END IF;
  PERFORM 1 FROM identity.organization_memberships m
  WHERE m.organization_id = p_actor_organization_id AND m.user_id = p_actor_user_id
    AND m.membership_status = 'ACTIVE';
  IF NOT FOUND THEN RAISE EXCEPTION 'Active organization membership required'; END IF;
  PERFORM 1 FROM identity.role_bindings rb
  WHERE rb.organization_id = p_actor_organization_id AND rb.subject_user_id = p_actor_user_id
    AND rb.binding_status = 'ACTIVE' AND rb.starts_at <= now()
    AND (rb.expires_at IS NULL OR rb.expires_at > now())
    AND rb.role_code IN ('S0_SOVEREIGN','B1_CEO','A3_PICARD','B2_MANAGER');
  IF NOT FOUND THEN RAISE EXCEPTION 'Order transition role required'; END IF;
  IF p_target_status = 'ACCEPTED' AND v_is_seller AND v_order.order_status = 'PLACED' THEN NULL;
  ELSIF p_target_status = 'REJECTED' AND v_is_seller AND v_order.order_status = 'PLACED' THEN NULL;
  ELSIF p_target_status = 'IN_PROGRESS' AND v_is_seller AND v_order.order_status = 'ACCEPTED' THEN NULL;
  ELSIF p_target_status = 'DELIVERED' AND v_is_seller AND v_order.order_status = 'IN_PROGRESS' THEN NULL;
  ELSIF p_target_status = 'ACCEPTED_BY_BUYER' AND v_is_buyer AND v_order.order_status = 'DELIVERED' THEN NULL;
  ELSIF p_target_status = 'DISPUTED' AND v_is_buyer AND v_order.order_status = 'DELIVERED' THEN NULL;
  ELSIF p_target_status = 'CANCELLED' AND (v_is_buyer OR v_is_seller)
        AND v_order.order_status IN ('PLACED','ACCEPTED','IN_PROGRESS') THEN NULL;
  ELSE RAISE EXCEPTION 'Invalid order transition: % -> %', v_order.order_status, p_target_status;
  END IF;
  UPDATE commerce.orders SET order_status = p_target_status, updated_at = now()
  WHERE id = p_order_id RETURNING * INTO v_order;
  SELECT coalesce(max(sequence_number),0)+1 INTO v_sequence
  FROM commerce.order_events WHERE order_id = p_order_id;
  INSERT INTO commerce.order_events (
    order_id,sequence_number,from_status,to_status,actor_type,
    actor_user_id,actor_organization_id,reason
  ) VALUES (
    p_order_id,v_sequence,
    (SELECT oe.to_status FROM commerce.order_events oe
     WHERE oe.order_id = p_order_id AND oe.sequence_number = v_sequence-1),
    p_target_status,'HUMAN',p_actor_user_id,p_actor_organization_id,p_reason
  );
  RETURN v_order;
END
$function$;

REVOKE ALL ON FUNCTION api.create_marketplace_order(uuid,uuid,uuid,text) FROM PUBLIC, anon, authenticated;
REVOKE ALL ON FUNCTION api.transition_marketplace_order(uuid,uuid,uuid,text,text) FROM PUBLIC, anon, authenticated;
GRANT EXECUTE ON FUNCTION api.create_marketplace_order(uuid,uuid,uuid,text) TO service_role;
GRANT EXECUTE ON FUNCTION api.transition_marketplace_order(uuid,uuid,uuid,text,text) TO service_role;
COMMIT;