terraform {
  required_providers {
    databricks = {
      source  = "databricks/databricks"
      version = "~> 1.29.0"
    }
  }
}

provider "databricks" {}

# Criamos o nosso Schema (Database) isolado para o projeto de MLOps do BACEN
resource "databricks_schema" "mlops_schema" {
  catalog_name = "workspace"
  name         = "bacen_mlops"
  comment      = "Schema gerenciado via Terraform para a esteira de MLOps - Prevenção BACEN"
}
