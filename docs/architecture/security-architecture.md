# Security Architecture

## Authentication & Authorization
- **User Authentication:** Centralized via AWS Cognito with MFA support
- **Service-to-Service Authorization:** JWT tokens for microservice communication
- **Role-Based Access Control:** Granular permissions based on user roles

## Network Security
- **Virtual Private Cloud (VPC):** All resources within private VPC
- **Subnets:** Private subnets for applications, public subnets for load balancers only
- **Security Groups:** Strict traffic control between components
- **Web Application Firewall (WAF):** AWS WAF for common exploit protection

## Data Encryption
- **Encryption in Transit:** TLS 1.2+ for all communications
- **Encryption at Rest:** AWS KMS for databases and storage

## SOP Data Protection
- **Dedicated S3 buckets** with restricted access
- **Strict IAM policies** for SOP data access
- **Audit logging** of all SOP access
- **Data retention policies** per client agreements