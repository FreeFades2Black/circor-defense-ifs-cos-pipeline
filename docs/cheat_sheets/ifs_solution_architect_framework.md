# Cheat Sheet: IFS ERP Solution Architect (Core Competencies & Architecture Framework)

## 1. Core Architecture Domains
* Functional Scope: Supply Chain Management (SCM), Manufacturing, Field Service Management (FSM), Finance, and Enterprise Asset Management (EAM).
* Platform Delivery: IFS Cloud (Aurena UI, containerized architecture, evergreen update cadence) vs IFS Applications 9/10 (EE client, Oracle PL/SQL foundational layer).
* Integration Frameworks:
  * IFS Connect (Message Routing, Inbound/Outbound adapters, SOAP/REST transformers).
  * IFS REST APIs (OData v4 specification, OAuth2 authentication, Swagger/OpenAPI documentation).
  * Enterprise Service Bus (ESB) / iPaaS patterns (Azure Integration Services, MuleSoft, Boomi).

## 2. Infrastructure, Security, and Governance
* Infrastructure: Kubernetes/container-based deployment models (IFS Cloud runs on Kubernetes via IFS Cloud Build Place), Oracle database optimization, hybrid on-premises to cloud connectivity.
* Identity & Access Management: OpenID Connect (OIDC), OAuth2, SAML 2.0 integration with enterprise IdPs (e.g., Microsoft Entra ID). Role-Based Access Control (RBAC) via IFS Permission Sets.
* Lifecycle Management: Use of IFS Build Place, IFS Lifecycle Experience portal, deliveries, service updates, and automated regression testing.

## 3. High-Value Architectural Scenarios & Decision Matrices

| Scenario | Architectural Approach | Key Trade-offs & Considerations |
| :--- | :--- | :--- |
| High-Volume IoT / Telemetry Ingestion | Decouple ingestion via an external buffer (Kafka, Event Hubs) -> Aggregate -> Push via OData APIs. | Prevents API connection exhaustion on the IFS middle tier. |
| Hybrid Identity & Multi-Company Security | Federate with enterprise IdP via OIDC; map security groups to IFS Permission Sets and Company Access limits. | Centralized de-provisioning; reduces administrative overhead and audit risk. |
| Legacy Database Integrations | Utilize IFS Connect with standard XML/JSON payloads; avoid direct Oracle DB table manipulation. | Direct table writes bypass IFS business logic and break upgrade compatibility. |
| Zero-Downtime Release Strategy | Implement service update pipelines in IFS Build Place using target delivery slots and automated validation runs. | Minimizes plant or warehouse downtime during scheduled IFS service update drops. |

## 4. Interview Strategy & Framing Points
* Strategic Leadership: Emphasize translating supply chain and shop-floor constraints into modular architectural patterns.
* System Governance: Highlight API versioning, change advisory board (CAB) reviews, and automated CI/CD gating for customizations.
* Vendor & Stakeholder Management: Frame coordination with third-party integrators, business process owners, and operational plant leadership to ensure business continuity.
