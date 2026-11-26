-- A'Space Business Marketplace — independent B2 / LD taxonomy blueprints
-- Global reference taxonomies. These are not tenant installations.
BEGIN;

CREATE TABLE areas.domain_blueprints (
  domain_code text PRIMARY KEY CHECK (domain_code ~ '^LD[0-9]{2}$'),
  domain_name text NOT NULL CHECK (length(btrim(domain_name)) > 0),
  description text NOT NULL CHECK (length(btrim(description)) > 0),
  mission text NOT NULL CHECK (length(btrim(mission)) > 0),
  sort_order smallint NOT NULL UNIQUE CHECK (sort_order BETWEEN 1 AND 8),
  taxonomy_version text NOT NULL DEFAULT '1.0.0',
  status text NOT NULL DEFAULT 'ACTIVE' CHECK (status IN ('ACTIVE','DEPRECATED')),
  created_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE enterprise.department_blueprints (
  department_code text PRIMARY KEY CHECK (department_code ~ '^B2\.[1-8]$'),
  department_name text NOT NULL CHECK (length(btrim(department_name)) > 0),
  description text NOT NULL CHECK (length(btrim(description)) > 0),
  mandate text NOT NULL CHECK (length(btrim(mandate)) > 0),
  sort_order smallint NOT NULL UNIQUE CHECK (sort_order BETWEEN 1 AND 8),
  taxonomy_version text NOT NULL DEFAULT '1.0.0',
  status text NOT NULL DEFAULT 'ACTIVE' CHECK (status IN ('ACTIVE','DEPRECATED')),
  created_at timestamptz NOT NULL DEFAULT now()
);

ALTER TABLE areas.domain_blueprints ENABLE ROW LEVEL SECURITY;
ALTER TABLE enterprise.department_blueprints ENABLE ROW LEVEL SECURITY;

REVOKE ALL ON TABLE areas.domain_blueprints FROM PUBLIC, anon, authenticated;
REVOKE ALL ON TABLE enterprise.department_blueprints FROM PUBLIC, anon, authenticated;
GRANT ALL ON TABLE areas.domain_blueprints TO service_role;
GRANT ALL ON TABLE enterprise.department_blueprints TO service_role;

CREATE INDEX domain_blueprints_status_order_idx
  ON areas.domain_blueprints (status, sort_order);
CREATE INDEX department_blueprints_status_order_idx
  ON enterprise.department_blueprints (status, sort_order);

INSERT INTO areas.domain_blueprints
  (domain_code, domain_name, description, mission, sort_order)
VALUES
  ('LD01','Business','Career, enterprise creation, business systems and value production.','Mission portfolio for building and operating ventures and business capabilities.',1),
  ('LD02','Finances','Financial sovereignty, capital, resources and long-term stewardship.','Mission portfolio for financial resilience and capital allocation.',2),
  ('LD03','Blue Life','Life, vitality and the conditions that sustain human flourishing.','Life portfolio; detailed substructure remains governed by the Life OS specification.',3),
  ('LD04','Meta Cognition','Learning, reflection, cognition, knowledge and personal evolution.','Mission portfolio for improving the quality of thinking and learning.',4),
  ('LD05','Sovereign Triangle','Sovereignty, autonomy and the systems that protect independent agency.','Mission portfolio for personal and systemic sovereignty.',5),
  ('LD06','Solarpunk Habitat','Habitat, ecology, circularity and regenerative living systems.','Mission portfolio for regenerative environments and infrastructure.',6),
  ('LD07','MC Sandbox','Experimental space for prototypes, exploration and controlled simulations.','Mission portfolio for experimentation without contaminating operational systems.',7),
  ('LD08','Civilizer / ABC OS','Civilizational systems, collective coordination and ABC OS initiatives.','Meta-project portfolio for long-horizon civilizational design and coordination.',8)
ON CONFLICT (domain_code) DO NOTHING;

INSERT INTO enterprise.department_blueprints
  (department_code, department_name, description, mandate, sort_order)
VALUES
  ('B2.1','Product & IP','Product portfolios, intellectual property, research and offer design.','Create and steward the assets and capabilities the Marketplace brings to market.',1),
  ('B2.2','Growth & Distribution','Brand, demand generation, audience, channels and distribution systems.','Create reach, discoverability and repeatable demand across the ecosystem.',2),
  ('B2.3','People & Talent','Talent, people operations, roles, learning and human-agent collaboration.','Compose the human and agent capabilities required to operate the business.',3),
  ('B2.4','Legal & Trust','Legal structure, contracts, privacy, trust, risk and compliance.','Establish the rules, protections and legitimacy under which value is exchanged.',4),
  ('B2.5','Tech & Intelligence','Platform engineering, data, compute, inference, memory and intelligence systems.','Build and operate the technical and intelligence substrate.',5),
  ('B2.6','Operations & Delivery','Service operations, production, fulfillment, quality and continuous improvement.','Turn offers and commitments into reliable delivered outcomes.',6),
  ('B2.7','Finance & Capital','Financial operations, capital allocation, accounting, treasury and unit economics.','Measure, allocate and steward the economic resources of the Marketplace.',7),
  ('B2.8','Sales & Partnerships','Sales, commercial relationships, alliances, suppliers and strategic partnerships.','Convert qualified demand into durable commercial relationships.',8)
ON CONFLICT (department_code) DO NOTHING;

COMMENT ON TABLE areas.domain_blueprints IS
  'Platform reference taxonomy for the eight A''Space Areas OS mission portfolios LD01–LD08. Not tenant-installed domains.';
COMMENT ON TABLE enterprise.department_blueprints IS
  'Platform reference taxonomy for the eight A''Space Business Marketplace departments B2.1–B2.8. Distinct from Areas OS portfolios.';
COMMENT ON COLUMN areas.domain_blueprints.domain_code IS
  'Stable Areas OS mission portfolio code; LD01 is Business and is not a Business Department.';
COMMENT ON COLUMN enterprise.department_blueprints.department_code IS
  'Stable Marketplace Business Department code; B2.1–B2.8 are distinct from LD01–LD08.';

COMMIT;
