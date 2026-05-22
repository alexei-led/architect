terraform {
  required_version = ">= 1.6.0"
}

# Provisions the same database the Helm chart hardcodes by hostname. The two
# tools own overlapping facts with no shared variable.
resource "aws_db_instance" "shop" {
  identifier        = "shop-db"
  engine            = "postgres"
  instance_class    = "db.t3.micro"
  allocated_storage = 20
  # Endpoint surfaces as shop-db.prod.internal, duplicated in helm/values.yaml.
}
