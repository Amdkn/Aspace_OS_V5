-- Canonical LD01 B1/B2/B3 holarchy, separate from Marketplace departments and LD portfolios.
BEGIN;

CREATE TABLE areas.holon_blueprints (
  holon_code text PRIMARY KEY CHECK (holon_code ~ '^B[1-3](\.[1-8])?$'),
  area_code text NOT NULL REFERENCES areas.domain_blueprints(domain_code) ON DELETE RESTRICT,
  holon_level smallint NOT NULL CHECK (holon_level BETWEEN 1 AND 3),
  holon_type text NOT NULL CHECK (holon_type IN ('OWNER_BOOK','TACTICAL_DC_MANAGER','MARVEL_EXECUTION_SQUAD')),
  display_name text NOT NULL CHECK (length(btrim(display_name)) > 0),
  mandate text NOT NULL CHECK (length(btrim(mandate)) > 0),
  parent_holon_code text REFERENCES areas.holon_blueprints(holon_code) ON DELETE RESTRICT,
  specialist_count smallint,
  runbook_required boolean NOT NULL DEFAULT false,
  source_path text NOT NULL,
  sort_order smallint NOT NULL,
  taxonomy_version text NOT NULL DEFAULT '1.0.0',
  status text NOT NULL DEFAULT 'ACTIVE' CHECK (status IN ('ACTIVE','DEPRECATED')),
  created_at timestamptz NOT NULL DEFAULT now(),
  UNIQUE (area_code, sort_order),
  CHECK (
    (holon_level = 1 AND parent_holon_code IS NULL)
    OR (holon_level IN (2,3) AND parent_holon_code IS NOT NULL)
  ),
  CHECK (
    (holon_type = 'OWNER_BOOK' AND holon_level = 1)
    OR (holon_type = 'TACTICAL_DC_MANAGER' AND holon_level = 2)
    OR (holon_type = 'MARVEL_EXECUTION_SQUAD' AND holon_level = 3 AND specialist_count = 7 AND runbook_required = true)
  )
);

ALTER TABLE areas.holon_blueprints ENABLE ROW LEVEL SECURITY;
REVOKE ALL ON TABLE areas.holon_blueprints FROM PUBLIC, anon, authenticated;
GRANT ALL ON TABLE areas.holon_blueprints TO service_role;

CREATE INDEX holon_blueprints_area_level_order_idx
  ON areas.holon_blueprints (area_code, holon_level, sort_order);

INSERT INTO areas.holon_blueprints
  (holon_code, area_code, holon_level, holon_type, display_name, mandate, parent_holon_code, specialist_count, runbook_required, source_path, sort_order, taxonomy_version)
VALUES
  ('B1','LD01',1,'OWNER_BOOK','B1-BOOK · OwnerBook','OwnerBook B1 · Carrière & Business — AMP A''Space Marketplace [C0] × The OMK Office [C2 1P] / SOB / Concordia.',NULL,NULL,false,'00_Memoire/bundle/areas_os/B_LD01_Business_AMP/README.md',1,'1.0.0'),
  ('B2.1','LD01',2,'TACTICAL_DC_MANAGER','B2.1 · Operations','Playbook patrimonial DC — Operations.','B1',NULL,false,'00_Memoire/bundle/areas_os/B_LD01_Business_AMP/B2_DC_Managers_Playbooks/README.md',2,'1.0.0'),
  ('B2.2','LD01',2,'TACTICAL_DC_MANAGER','B2.2 · Trésorerie','Playbook patrimonial DC — Trésorerie.','B1',NULL,false,'00_Memoire/bundle/areas_os/B_LD01_Business_AMP/B2_DC_Managers_Playbooks/README.md',3,'1.0.0'),
  ('B2.3','LD01',2,'TACTICAL_DC_MANAGER','B2.3 · Legal','Playbook patrimonial DC — Legal.','B1',NULL,false,'00_Memoire/bundle/areas_os/B_LD01_Business_AMP/B2_DC_Managers_Playbooks/README.md',4,'1.0.0'),
  ('B2.4','LD01',2,'TACTICAL_DC_MANAGER','B2.4 · R&D','Playbook patrimonial DC — R&D.','B1',NULL,false,'00_Memoire/bundle/areas_os/B_LD01_Business_AMP/B2_DC_Managers_Playbooks/README.md',5,'1.0.0'),
  ('B2.5','LD01',2,'TACTICAL_DC_MANAGER','B2.5 · Alliances','Playbook patrimonial DC — Alliances.','B1',NULL,false,'00_Memoire/bundle/areas_os/B_LD01_Business_AMP/B2_DC_Managers_Playbooks/README.md',6,'1.0.0'),
  ('B2.6','LD01',2,'TACTICAL_DC_MANAGER','B2.6 · Infra','Playbook patrimonial DC — Infra.','B1',NULL,false,'00_Memoire/bundle/areas_os/B_LD01_Business_AMP/B2_DC_Managers_Playbooks/README.md',7,'1.0.0'),
  ('B2.7','LD01',2,'TACTICAL_DC_MANAGER','B2.7 · IT','Playbook patrimonial DC — IT.','B1',NULL,false,'00_Memoire/bundle/areas_os/B_LD01_Business_AMP/B2_DC_Managers_Playbooks/README.md',8,'1.0.0'),
  ('B2.8','LD01',2,'TACTICAL_DC_MANAGER','B2.8 · Gouvernance','Playbook patrimonial DC — Gouvernance.','B1',NULL,false,'00_Memoire/bundle/areas_os/B_LD01_Business_AMP/B2_DC_Managers_Playbooks/README.md',9,'1.0.0'),
  ('B3.1','LD01',3,'MARVEL_EXECUTION_SQUAD','B3.1 · Marvel Squad','Squad d’exécution composée de 7 spécialistes et d’un runbook opérationnel.','B1',7,true,'00_Memoire/bundle/areas_os/B_LD01_Business_AMP/B3_Marvel_Squads_Runbooks/README.md',10,'1.0.0'),
  ('B3.2','LD01',3,'MARVEL_EXECUTION_SQUAD','B3.2 · Marvel Squad','Squad d’exécution composée de 7 spécialistes et d’un runbook opérationnel.','B1',7,true,'00_Memoire/bundle/areas_os/B_LD01_Business_AMP/B3_Marvel_Squads_Runbooks/README.md',11,'1.0.0'),
  ('B3.3','LD01',3,'MARVEL_EXECUTION_SQUAD','B3.3 · Marvel Squad','Squad d’exécution composée de 7 spécialistes et d’un runbook opérationnel.','B1',7,true,'00_Memoire/bundle/areas_os/B_LD01_Business_AMP/B3_Marvel_Squads_Runbooks/README.md',12,'1.0.0'),
  ('B3.4','LD01',3,'MARVEL_EXECUTION_SQUAD','B3.4 · Marvel Squad','Squad d’exécution composée de 7 spécialistes et d’un runbook opérationnel.','B1',7,true,'00_Memoire/bundle/areas_os/B_LD01_Business_AMP/B3_Marvel_Squads_Runbooks/README.md',13,'1.0.0'),
  ('B3.5','LD01',3,'MARVEL_EXECUTION_SQUAD','B3.5 · Marvel Squad','Squad d’exécution composée de 7 spécialistes et d’un runbook opérationnel.','B1',7,true,'00_Memoire/bundle/areas_os/B_LD01_Business_AMP/B3_Marvel_Squads_Runbooks/README.md',14,'1.0.0'),
  ('B3.6','LD01',3,'MARVEL_EXECUTION_SQUAD','B3.6 · Marvel Squad','Squad d’exécution composée de 7 spécialistes et d’un runbook opérationnel.','B1',7,true,'00_Memoire/bundle/areas_os/B_LD01_Business_AMP/B3_Marvel_Squads_Runbooks/README.md',15,'1.0.0'),
  ('B3.7','LD01',3,'MARVEL_EXECUTION_SQUAD','B3.7 · Marvel Squad','Squad d’exécution composée de 7 spécialistes et d’un runbook opérationnel.','B1',7,true,'00_Memoire/bundle/areas_os/B_LD01_Business_AMP/B3_Marvel_Squads_Runbooks/README.md',16,'1.0.0'),
  ('B3.8','LD01',3,'MARVEL_EXECUTION_SQUAD','B3.8 · Marvel Squad','Squad d’exécution composée de 7 spécialistes et d’un runbook opérationnel.','B1',7,true,'00_Memoire/bundle/areas_os/B_LD01_Business_AMP/B3_Marvel_Squads_Runbooks/README.md',17,'1.0.0');

COMMENT ON TABLE areas.holon_blueprints IS
  'Canonical LD01 B1/B2/B3 holarchy reference. These are structural blueprints, not Marketplace departments or tenant agent instances.';
COMMENT ON COLUMN areas.holon_blueprints.parent_holon_code IS
  'Canonical delegation parent from the LD01 B1-BOOK AGENTS.md; B2 and B3 are both direct B1 subordinates.';
COMMENT ON COLUMN areas.holon_blueprints.specialist_count IS
  'Seven specialists per B3 Marvel squad as specified in the canonical B3 runbook README; specialist identities are not modeled here.';
COMMENT ON COLUMN areas.holon_blueprints.source_path IS
  'Canonical source path in Amdkn/Aspace_OS_V5 used to ground this blueprint.';

COMMIT;
