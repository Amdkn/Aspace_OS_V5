-- Correct the taxonomy collision: B2.1–B2.8 are LD01 tactical DC managers,
-- not the eight Business Marketplace departments.
BEGIN;

ALTER TABLE enterprise.department_blueprints
  RENAME COLUMN department_code TO department_key;

ALTER TABLE enterprise.department_blueprints
  DROP CONSTRAINT IF EXISTS department_blueprints_department_code_check;

DELETE FROM enterprise.department_blueprints;

ALTER TABLE enterprise.department_blueprints
  ADD CONSTRAINT department_blueprints_department_key_check
  CHECK (department_key ~ '^[a-z0-9]+(-[a-z0-9]+)*$');

INSERT INTO enterprise.department_blueprints
  (department_key, department_name, description, mandate, sort_order, taxonomy_version, status)
VALUES
  ('product-ip','Product & IP','Product portfolios, intellectual property, research and offer design.','Create and steward the assets and capabilities the Marketplace brings to market.',1,'1.0.1','ACTIVE'),
  ('growth-distribution','Growth & Distribution','Brand, demand generation, audience, channels and distribution systems.','Create reach, discoverability and repeatable demand across the ecosystem.',2,'1.0.1','ACTIVE'),
  ('people-talent','People & Talent','Talent, people operations, roles, learning and human-agent collaboration.','Compose the human and agent capabilities required to operate the business.',3,'1.0.1','ACTIVE'),
  ('legal-trust','Legal & Trust','Legal structure, contracts, privacy, trust, risk and compliance.','Establish the rules, protections and legitimacy under which value is exchanged.',4,'1.0.1','ACTIVE'),
  ('tech-intelligence','Tech & Intelligence','Platform engineering, data, compute, inference, memory and intelligence systems.','Build and operate the technical and intelligence substrate.',5,'1.0.1','ACTIVE'),
  ('operations-delivery','Operations & Delivery','Service operations, production, fulfillment, quality and continuous improvement.','Turn offers and commitments into reliable delivered outcomes.',6,'1.0.1','ACTIVE'),
  ('finance-capital','Finance & Capital','Financial operations, capital allocation, accounting, treasury and unit economics.','Measure, allocate and steward the economic resources of the Marketplace.',7,'1.0.1','ACTIVE'),
  ('sales-partnerships','Sales & Partnerships','Sales, commercial relationships, alliances, suppliers and strategic partnerships.','Convert qualified demand into durable commercial relationships.',8,'1.0.1','ACTIVE');

COMMENT ON TABLE enterprise.department_blueprints IS
  'Platform reference taxonomy for the eight Business Marketplace operating departments. These are not the B2.1–B2.8 DC managers inside Areas OS LD01.';
COMMENT ON COLUMN enterprise.department_blueprints.department_key IS
  'Stable technical key for a Marketplace operating department; intentionally distinct from LD01 holon codes B2.1–B2.8.';

COMMIT;
