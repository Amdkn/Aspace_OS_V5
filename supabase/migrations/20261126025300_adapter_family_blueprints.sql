-- Global adapter-family reference catalog for the Marketplace Control Plane.
BEGIN;

CREATE TABLE integration.adapter_family_blueprints (
  family_key text PRIMARY KEY CHECK (family_key ~ '^[a-z0-9]+(-[a-z0-9]+)*$'),
  family_name text NOT NULL CHECK (length(btrim(family_name)) > 0),
  provider_examples text[] NOT NULL DEFAULT ARRAY[]::text[],
  icon_key text NOT NULL,
  sort_order smallint NOT NULL UNIQUE CHECK (sort_order BETWEEN 1 AND 20),
  taxonomy_version text NOT NULL DEFAULT '1.0.0',
  implementation_status text NOT NULL DEFAULT 'PLANNED'
    CHECK (implementation_status IN ('PLANNED','IN_PROGRESS','AVAILABLE','DEPRECATED')),
  created_at timestamptz NOT NULL DEFAULT now()
);

ALTER TABLE integration.adapter_family_blueprints ENABLE ROW LEVEL SECURITY;
REVOKE ALL ON TABLE integration.adapter_family_blueprints FROM PUBLIC, anon, authenticated;
GRANT ALL ON TABLE integration.adapter_family_blueprints TO service_role;

CREATE INDEX adapter_family_blueprints_status_order_idx
  ON integration.adapter_family_blueprints (implementation_status, sort_order);

INSERT INTO integration.adapter_family_blueprints
  (family_key, family_name, provider_examples, icon_key, sort_order, taxonomy_version, implementation_status)
VALUES
  ('identity-access','Identity & access',ARRAY['Google Workspace','Microsoft 365','Auth0','Clerk'],'ShieldCheck',1,'1.0.0','PLANNED'),
  ('communication','Communication',ARRAY['Gmail','Outlook','Slack','Google Chat','Teams','Discord'],'Zap',2,'1.0.0','PLANNED'),
  ('calendar-scheduling','Calendar & scheduling',ARRAY['Google Calendar','Microsoft Calendar','Cal.com'],'Activity',3,'1.0.0','PLANNED'),
  ('files-knowledge','Files & knowledge',ARRAY['Google Drive','OneDrive','Notion','Confluence'],'FileText',4,'1.0.0','PLANNED'),
  ('work-management','Work management',ARRAY['Linear','ClickUp','Jira','GitHub Projects'],'Workflow',5,'1.0.0','PLANNED'),
  ('source-control-delivery','Source control & delivery',ARRAY['GitHub','GitLab','Bitbucket','Vercel'],'GitBranch',6,'1.0.0','PLANNED'),
  ('data-backend','Data & backend',ARRAY['Supabase','PostgreSQL','Redis','Object Storage'],'Database',7,'1.0.0','PLANNED'),
  ('automation','Automation',ARRAY['n8n','Make','Zapier','Temporal'],'Blocks',8,'1.0.0','PLANNED'),
  ('ai-model-providers','AI model providers',ARRAY['OpenAI','Anthropic','Gemini','Local endpoints'],'Sparkles',9,'1.0.0','PLANNED'),
  ('agent-protocols','Agent protocols',ARRAY['MCP','A2A','Composio','Custom tool gateways'],'Network',10,'1.0.0','PLANNED'),
  ('finance-commerce','Finance & commerce',ARRAY['Stripe','Billing','Accounting','Invoicing'],'CreditCard',11,'1.0.0','PLANNED'),
  ('crm-revenue','CRM & revenue',ARRAY['HubSpot','Salesforce','Pipedrive'],'BriefcaseBusiness',12,'1.0.0','PLANNED'),
  ('customer-support','Customer support',ARRAY['Intercom','Zendesk','Help Scout'],'Compass',13,'1.0.0','PLANNED'),
  ('analytics-observability','Analytics & observability',ARRAY['PostHog','Sentry','OpenTelemetry'],'Activity',14,'1.0.0','PLANNED'),
  ('documents-signatures','Documents & signatures',ARRAY['DocuSign','Dropbox Sign','PDF services'],'FileText',15,'1.0.0','PLANNED'),
  ('commerce-catalog','Commerce & catalog',ARRAY['Shopify','WooCommerce','Product feeds'],'Layers3',16,'1.0.0','PLANNED'),
  ('people-operations','People operations',ARRAY['HRIS','Recruiting','Payroll providers'],'Building2',17,'1.0.0','PLANNED'),
  ('maps-mobility','Maps & mobility',ARRAY['Google Maps','Mapbox','Routing APIs'],'Globe2',18,'1.0.0','PLANNED'),
  ('iot-physical-systems','IoT & physical systems',ARRAY['MQTT','Device gateways','Telemetry'],'Zap',19,'1.0.0','PLANNED'),
  ('storage-portability','Storage & portability',ARRAY['S3-compatible','Backup','Export','Archive'],'Cloud',20,'1.0.0','PLANNED');

COMMENT ON TABLE integration.adapter_family_blueprints IS
  'Global reference catalog of 20 adapter families and provider examples. Entries are design blueprints, not implemented or connected integrations.';
COMMENT ON COLUMN integration.adapter_family_blueprints.provider_examples IS
  'Provider/product examples from the Marketplace architecture. These values do not imply a shipped adapter or verified connection.';
COMMENT ON COLUMN integration.adapter_family_blueprints.implementation_status IS
  'Lifecycle of the adapter family implementation; PLANNED does not mean provider connection is available.';

COMMIT;
