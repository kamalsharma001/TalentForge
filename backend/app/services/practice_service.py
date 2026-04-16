"""
PracticeService — manages the practice question bank.

Features:
1. Lists questions with filtering by job_role, difficulty, category
2. Retrieves single question
3. Creates new questions (admin)
4. Seeds initial question bank (admin) — safe to re-run, adds only missing questions
"""

import logging

from app import db
from app.models.practice_question import PracticeQuestion
from app.utils.errors import NotFoundError
from app.utils.pagination import paginate_query
from app.schemas.practice_schema import PracticeQuestionSchema

logger = logging.getLogger(__name__)


SEED_QUESTIONS = [

    # ═══════════════════════════════════════════════════════════════
    # SOFTWARE ENGINEER
    # ═══════════════════════════════════════════════════════════════
    {
        "question": "Tell me about yourself and your background in software development.",
        "job_role": "Software Engineer",
        "difficulty": "easy",
        "category": "behavioral",
        "hint": "Focus on your journey, key projects, and what motivates you.",
        "sample_answer": "I started programming in college with Python and have spent the last three years building web applications. My most recent role involved developing a microservices-based e-commerce platform where I was responsible for the payment and inventory services. I enjoy solving complex problems and collaborating with cross-functional teams.",
    },
    {
        "question": "Describe a time when you had to learn a new technology quickly for a project.",
        "job_role": "Software Engineer",
        "difficulty": "easy",
        "category": "behavioral",
        "hint": "Use the STAR method: Situation, Task, Action, Result.",
        "sample_answer": "When our team decided to migrate from REST to GraphQL, I volunteered to lead the proof of concept. I spent a weekend going through the official docs and built a small prototype. Within two weeks, I had migrated our main product catalog endpoint, reducing over-fetching by 40%.",
    },
    {
        "question": "How do you handle disagreements with teammates about technical decisions?",
        "job_role": "Software Engineer",
        "difficulty": "easy",
        "category": "behavioral",
        "hint": "Emphasize collaboration, data-driven decisions, and respect.",
        "sample_answer": "I focus on understanding their perspective first, then present data or prototypes to support my view. In one case, a teammate and I disagreed on database choice. We agreed to benchmark both options against our actual query patterns, and the data clearly pointed to PostgreSQL, which we both accepted.",
    },
    {
        "question": "Tell me about a project that failed or didn't go as planned. What did you learn?",
        "job_role": "Software Engineer",
        "difficulty": "medium",
        "category": "behavioral",
        "hint": "Be honest about the failure; focus on lessons learned and growth.",
        "sample_answer": "We launched a real-time analytics feature without adequate load testing. It crashed under peak traffic on launch day. I learned the importance of production-like testing environments and championed the adoption of load testing in our CI pipeline afterward.",
    },
    {
        "question": "Describe a situation where you had competing priorities. How did you manage them?",
        "job_role": "Software Engineer",
        "difficulty": "medium",
        "category": "behavioral",
        "hint": "Show structured prioritisation, communication with stakeholders, and trade-off thinking.",
        "sample_answer": "During a major release I was asked to fix a production bug and finish a new feature simultaneously. I communicated the conflict to my manager, triaged the bug severity, and we agreed to hot-fix the bug first. I documented the feature's state so another engineer could pick it up if needed, and we shipped both within the sprint.",
    },
    {
        "question": "Tell me about the most complex technical problem you've solved. Walk me through your approach.",
        "job_role": "Software Engineer",
        "difficulty": "hard",
        "category": "behavioral",
        "hint": "Demonstrate systematic debugging, trade-off analysis, and clear communication.",
        "sample_answer": "We had a memory leak in a Node.js service that only appeared under sustained load. I used heap snapshots and Chrome DevTools to trace the leak to an event listener that was never detached. I introduced a teardown lifecycle hook and added automated memory-regression tests to our CI suite.",
    },
    {
        "question": "Explain the difference between an array and a linked list. When would you use each?",
        "job_role": "Software Engineer",
        "difficulty": "easy",
        "category": "technical",
        "hint": "Think about memory layout, access patterns, and insertion/deletion costs.",
        "sample_answer": "Arrays provide O(1) random access and cache-friendly memory layout, making them ideal for read-heavy workloads. Linked lists offer O(1) insertion and deletion at known positions but O(n) access time. I would choose arrays for most cases unless I need frequent insertions/deletions at arbitrary positions.",
    },
    {
        "question": "What is the difference between a stack and a queue? Give real-world examples.",
        "job_role": "Software Engineer",
        "difficulty": "easy",
        "category": "technical",
        "hint": "Think LIFO vs FIFO and practical applications.",
        "sample_answer": "A stack is LIFO — used for undo operations, call stacks, and expression evaluation. A queue is FIFO — used for task scheduling, BFS traversal, and message processing. A print spooler uses a queue; a browser's back button uses a stack.",
    },
    {
        "question": "Explain how a hash map works internally. What happens during a collision?",
        "job_role": "Software Engineer",
        "difficulty": "medium",
        "category": "technical",
        "hint": "Cover hashing, buckets, collision strategies, and load factor.",
        "sample_answer": "A hash map uses a hash function to map keys to bucket indices. On collision, common strategies are chaining (linked lists at each bucket) or open addressing (probing for the next empty slot). When the load factor exceeds ~0.75, the array is resized and all entries are rehashed.",
    },
    {
        "question": "Implement an LRU cache with O(1) get and put. Describe your data structure choices.",
        "job_role": "Software Engineer",
        "difficulty": "hard",
        "category": "technical",
        "hint": "Combine a hash map with a doubly-linked list.",
        "sample_answer": "Use a hash map for O(1) key lookup and a doubly-linked list to maintain access order. On get(), move the node to the head. On put(), add to head; if capacity is exceeded, evict the tail node. Both operations are O(1) since we have direct pointers from the hash map.",
    },
    {
        "question": "Design a URL shortening service like bit.ly. What are the main components?",
        "job_role": "Software Engineer",
        "difficulty": "easy",
        "category": "system_design",
        "hint": "Think about encoding, storage, redirection, and analytics.",
        "sample_answer": "Main components: an API server for creating/resolving short URLs, a database mapping short codes to original URLs, and a redirection service. Use base62 encoding of an auto-incrementing ID. Add a Redis cache for popular URLs and an analytics pipeline for click tracking.",
    },
    {
        "question": "How would you design a real-time chat application? Consider scalability and delivery guarantees.",
        "job_role": "Software Engineer",
        "difficulty": "medium",
        "category": "system_design",
        "hint": "Think about WebSockets, message persistence, presence, and horizontal scaling.",
        "sample_answer": "Use WebSocket connections for real-time communication. Store messages in PostgreSQL (metadata) and Cassandra (message history). Use Redis Pub/Sub for cross-server message routing. Implement message acknowledgment for delivery guarantees and a presence service using heartbeats.",
    },
    {
        "question": "Design a distributed task scheduler that can handle millions of scheduled jobs with fault tolerance.",
        "job_role": "Software Engineer",
        "difficulty": "hard",
        "category": "system_design",
        "hint": "Think about partitioning, leader election, idempotency, and dead-letter queues.",
        "sample_answer": "Partition jobs by schedule time across multiple worker groups. Use a distributed lock (ZooKeeper/etcd) for leader election within each partition. The leader polls for due jobs and dispatches them to a message queue. Workers process idempotently. Failed jobs go to a dead-letter queue with alerting.",
    },

    # ═══════════════════════════════════════════════════════════════
    # SENIOR SOFTWARE ENGINEER
    # ═══════════════════════════════════════════════════════════════
    {
        "question": "Describe a situation where you had to mentor a junior developer. What approach did you take?",
        "job_role": "Senior Software Engineer",
        "difficulty": "medium",
        "category": "behavioral",
        "hint": "Focus on your teaching style, patience, and measurable outcomes.",
        "sample_answer": "I paired with a junior developer for code reviews and dedicated 30 minutes daily for knowledge-sharing sessions. I focused on explaining the 'why' behind patterns. Within three months, their PR approval rate improved from 40% to 85% on first review.",
    },
    {
        "question": "Describe a time when you had to push back on a product requirement due to technical constraints.",
        "job_role": "Senior Software Engineer",
        "difficulty": "hard",
        "category": "behavioral",
        "hint": "Demonstrate diplomacy, technical communication, and solution orientation.",
        "sample_answer": "The product team wanted real-time search across 50M records with sub-100ms latency. I prepared a comparison showing cost and timeline for Elasticsearch vs. PostgreSQL full-text search. I presented three options with trade-offs and we agreed on a phased approach.",
    },
    {
        "question": "Explain the CAP theorem and how it applies to distributed database design.",
        "job_role": "Senior Software Engineer",
        "difficulty": "hard",
        "category": "technical",
        "hint": "C=Consistency, A=Availability, P=Partition Tolerance. Discuss real systems.",
        "sample_answer": "The CAP theorem states a distributed system can guarantee at most two of three: Consistency, Availability, Partition Tolerance. Since network partitions are inevitable, the real choice is between CP and AP. MongoDB (with majority write concern) is CP; Cassandra is AP with eventual consistency.",
    },
    {
        "question": "Design a content delivery network (CDN) from scratch. How do you handle cache invalidation?",
        "job_role": "Senior Software Engineer",
        "difficulty": "hard",
        "category": "system_design",
        "hint": "Cover edge servers, cache hierarchy, TTL policies, and DNS-based routing.",
        "sample_answer": "Deploy edge servers in multiple regions. Use GeoDNS or anycast routing to direct users to the nearest edge. Implement a two-tier cache: edge and mid-tier shield. Use TTL-based expiration with a purge API for explicit invalidation. Monitor cache hit ratios per region.",
    },
    {
        "question": "How do you approach code reviews in your team? What do you prioritise?",
        "job_role": "Senior Software Engineer",
        "difficulty": "easy",
        "category": "behavioral",
        "hint": "Mention correctness, readability, security, performance, and team culture.",
        "sample_answer": "I prioritise correctness first, then readability and maintainability. I look for security issues, proper error handling, and test coverage. I frame feedback as questions ('What if X happens here?') rather than commands to keep the tone collaborative and constructive.",
    },

    # ═══════════════════════════════════════════════════════════════
    # STAFF ENGINEER
    # ═══════════════════════════════════════════════════════════════
    {
        "question": "How do you influence engineering decisions across teams when you don't have direct authority?",
        "job_role": "Staff Engineer",
        "difficulty": "hard",
        "category": "behavioral",
        "hint": "Talk about persuasion through data, building trust, and aligning on company goals.",
        "sample_answer": "I rely on writing well-reasoned RFCs, presenting trade-offs clearly, and finding champions in each team. I listen to objections and incorporate valid concerns into the proposal. Trust is built over repeated positive outcomes, not titles.",
    },
    {
        "question": "Describe a time you identified and resolved a systemic engineering problem across multiple teams.",
        "job_role": "Staff Engineer",
        "difficulty": "hard",
        "category": "behavioral",
        "hint": "Show cross-functional thinking, root-cause analysis, and organisational impact.",
        "sample_answer": "I noticed five teams were each building their own internal metrics pipelines. I ran an audit, documented the redundancy, and proposed a shared observability platform. I co-designed it with reps from each team and drove adoption by providing migration guides and office hours.",
    },
    {
        "question": "Explain the difference between horizontal and vertical scaling and when to choose each.",
        "job_role": "Staff Engineer",
        "difficulty": "easy",
        "category": "technical",
        "hint": "Consider cost, fault tolerance, state management, and bottlenecks.",
        "sample_answer": "Vertical scaling (bigger servers) is simpler but has a ceiling and a single point of failure. Horizontal scaling (more servers) gives fault tolerance and near-unlimited scale at the cost of distributed-systems complexity. Stateless services scale horizontally easily; stateful services require sharding or distributed state management.",
    },
    {
        "question": "Design a global payment processing platform. Address reliability, compliance, and latency.",
        "job_role": "Staff Engineer",
        "difficulty": "hard",
        "category": "system_design",
        "hint": "Consider idempotency, PCI-DSS, regional failover, and exactly-once semantics.",
        "sample_answer": "Use a multi-region active-active architecture with regional write affinity to minimise latency. Store transactions in a globally-consistent database (Spanner/CockroachDB). Implement idempotency keys to prevent double-charges. Encrypt all card data at rest/transit; tokenise PANs. Use circuit breakers toward payment gateways and automated reconciliation jobs.",
    },
    {
        "question": "What strategies do you use to manage technical debt without halting feature delivery?",
        "job_role": "Staff Engineer",
        "difficulty": "medium",
        "category": "behavioral",
        "hint": "Balance business value with long-term maintainability.",
        "sample_answer": "I categorise debt by impact (performance, security, dev velocity) and track it in a dedicated backlog. I negotiate 20% of each sprint for debt reduction and bundle refactors with related feature work. Transparent metrics—like deploy frequency and MTTR—make the ROI of debt paydown visible to leadership.",
    },

    # ═══════════════════════════════════════════════════════════════
    # BACKEND ENGINEER
    # ═══════════════════════════════════════════════════════════════
    {
        "question": "Explain the difference between synchronous and asynchronous processing. When do you use each?",
        "job_role": "Backend Engineer",
        "difficulty": "easy",
        "category": "technical",
        "hint": "Think about latency tolerance, throughput, and user experience.",
        "sample_answer": "Synchronous processing blocks until a result is returned—good for simple CRUD operations. Asynchronous processing (message queues, background workers) decouples producers from consumers, improving throughput and resilience for tasks like email sending, video encoding, or report generation.",
    },
    {
        "question": "Explain the concept of database indexing. How does a B-tree index work, and what are the trade-offs?",
        "job_role": "Backend Engineer",
        "difficulty": "medium",
        "category": "technical",
        "hint": "Discuss read performance vs write overhead and when indexes help vs hurt.",
        "sample_answer": "A B-tree index is a balanced tree where each node can have multiple children. It keeps data sorted, enabling searches, insertions, and deletions in O(log n). Indexes dramatically speed up reads but add overhead to writes since the index must be updated. Too many indexes slow INSERT/UPDATE operations.",
    },
    {
        "question": "How would you optimise a slow-running SQL query on a table with 100 million rows?",
        "job_role": "Backend Engineer",
        "difficulty": "medium",
        "category": "technical",
        "hint": "Mention EXPLAIN ANALYZE, indexes, query rewriting, and partitioning.",
        "sample_answer": "I'd start with EXPLAIN ANALYZE to find sequential scans or nested-loop joins. I'd add or adjust indexes, rewrite subqueries as CTEs, ensure predicates are SARGable, and consider table partitioning by date for range queries. For read-heavy tables I might add a materialised view or a read replica.",
    },
    {
        "question": "Design a notification system supporting email, SMS, and push notifications.",
        "job_role": "Backend Engineer",
        "difficulty": "medium",
        "category": "system_design",
        "hint": "Think about message queues, channel abstraction, retry logic, and user preferences.",
        "sample_answer": "Use a message queue (RabbitMQ/SQS) to decouple notification creation from delivery. Define a channel interface with Email, SMS, and Push implementations. Store user preferences in the DB. A dispatcher reads from the queue, checks preferences, and routes to the appropriate handler. Add exponential-backoff retry for failed deliveries.",
    },
    {
        "question": "How do you approach API versioning in a backend service?",
        "job_role": "Backend Engineer",
        "difficulty": "easy",
        "category": "technical",
        "hint": "Mention URL versioning, header versioning, backward compatibility, and deprecation policies.",
        "sample_answer": "I prefer URL prefix versioning (/v1/, /v2/) for visibility. I maintain at least one previous version concurrently and provide a deprecation timeline. Breaking changes always warrant a new version; additive changes (new optional fields) can go into the same version. I document changes in a CHANGELOG and notify consumers via email.",
    },
    {
        "question": "Tell me about a time you improved the performance of a backend service significantly.",
        "job_role": "Backend Engineer",
        "difficulty": "medium",
        "category": "behavioral",
        "hint": "Use STAR. Be specific about metrics before and after.",
        "sample_answer": "Our recommendations API had P99 latency of 2.4 s. I profiled it with py-spy and found 80% of time was spent in repeated DB queries inside a loop. I replaced the loop with a single bulk query and added Redis caching with a 5-minute TTL. P99 dropped to 180 ms—a 13x improvement.",
    },
    {
        "question": "Design a rate-limiting system for a public API with millions of requests per day.",
        "job_role": "Backend Engineer",
        "difficulty": "hard",
        "category": "system_design",
        "hint": "Cover token bucket vs sliding window, Redis, distributed counters, and response headers.",
        "sample_answer": "Use a sliding-window counter in Redis keyed by (user_id, minute). On each request, increment the counter with an expiry equal to the window size. If the count exceeds the threshold, return 429 with Retry-After. For distributed deployments, use Redis + Lua scripts for atomic increment-and-check to prevent race conditions.",
    },

    # ═══════════════════════════════════════════════════════════════
    # FRONTEND ENGINEER
    # ═══════════════════════════════════════════════════════════════
    {
        "question": "Explain the virtual DOM and why React uses it.",
        "job_role": "Frontend Engineer",
        "difficulty": "easy",
        "category": "technical",
        "hint": "Cover reconciliation, diffing, and performance benefits.",
        "sample_answer": "The virtual DOM is a lightweight in-memory representation of the real DOM. React computes the diff between the old and new virtual DOM trees (reconciliation) and only applies minimal real DOM mutations. This batching avoids costly reflows and repaints on every state change.",
    },
    {
        "question": "What are the differences between CSS Flexbox and Grid? When do you use each?",
        "job_role": "Frontend Engineer",
        "difficulty": "easy",
        "category": "technical",
        "hint": "Think 1D vs 2D layout and common use cases.",
        "sample_answer": "Flexbox is a 1D layout model—great for rows or columns of items like navbars, card lists, or form controls. CSS Grid is 2D—ideal for page-level layouts with rows and columns simultaneously. I use Flexbox for component-level alignment and Grid for overall page structure.",
    },
    {
        "question": "Explain how the browser renders a web page from HTML to pixels.",
        "job_role": "Frontend Engineer",
        "difficulty": "medium",
        "category": "technical",
        "hint": "Cover DOM construction, CSSOM, render tree, layout, paint, and compositing.",
        "sample_answer": "The browser parses HTML into a DOM tree and CSS into a CSSOM tree. These are combined into a render tree (only visible nodes). The layout step computes geometry; paint generates pixel layers; compositing merges layers using the GPU. Reflows (layout changes) are expensive; repaints (color changes) are cheaper.",
    },
    {
        "question": "Describe a performance optimisation you implemented on a frontend application.",
        "job_role": "Frontend Engineer",
        "difficulty": "medium",
        "category": "behavioral",
        "hint": "Use STAR. Mention specific tools—Lighthouse, WebPageTest, bundle analyser.",
        "sample_answer": "Our React app's initial bundle was 1.8 MB. I used Webpack Bundle Analyzer to identify unused lodash methods, switched to lodash-es with tree shaking, added route-based code splitting, and lazy-loaded images. The bundle dropped to 420 KB and LCP improved by 1.8 seconds.",
    },
    {
        "question": "How do you ensure a web application is accessible (a11y)?",
        "job_role": "Frontend Engineer",
        "difficulty": "medium",
        "category": "technical",
        "hint": "Mention WCAG, ARIA, keyboard navigation, colour contrast, and screen-reader testing.",
        "sample_answer": "I follow WCAG 2.1 AA guidelines: proper heading hierarchy, ARIA labels for interactive elements, minimum 4.5:1 colour contrast ratio, full keyboard navigability, and focus management for modals. I use axe-core in CI and test with NVDA/VoiceOver manually.",
    },
    {
        "question": "Design a design system for a large-scale frontend application used by multiple product teams.",
        "job_role": "Frontend Engineer",
        "difficulty": "hard",
        "category": "system_design",
        "hint": "Cover token architecture, component API contracts, versioning, and adoption strategy.",
        "sample_answer": "Build a token layer (colour, spacing, typography) as CSS custom properties synced from Figma via Style Dictionary. Publish a component library (React + Storybook) on an internal npm registry with semantic versioning. Provide a migration guide per major version and a deprecation lint rule to flag old usage. Assign a design-system team to triage issues and publish a monthly changelog.",
    },
    {
        "question": "How would you handle state management in a large React application?",
        "job_role": "Frontend Engineer",
        "difficulty": "hard",
        "category": "technical",
        "hint": "Compare Context, Redux, Zustand, React Query, and when to use each.",
        "sample_answer": "I separate server state (React Query / SWR — caching, refetching, background sync) from client UI state (Zustand or Redux Toolkit for complex shared state, local useState for isolated UI). Context is fine for low-frequency updates like theme or auth. Avoiding a single global store for everything prevents unnecessary re-renders.",
    },

    # ═══════════════════════════════════════════════════════════════
    # FULL STACK ENGINEER
    # ═══════════════════════════════════════════════════════════════
    {
        "question": "How do you decide where to put business logic — frontend, backend, or database?",
        "job_role": "Full Stack Engineer",
        "difficulty": "medium",
        "category": "technical",
        "hint": "Consider security, duplication, performance, and maintainability.",
        "sample_answer": "Security-sensitive logic (auth, pricing, access control) always lives in the backend. Validation logic is duplicated on both sides—frontend for UX, backend as the source of truth. Heavy computation or complex joins live in the database or a service. Simple display logic (formatting, sorting already-fetched data) is fine on the frontend.",
    },
    {
        "question": "Walk me through how you'd build a full-stack feature from requirements to production.",
        "job_role": "Full Stack Engineer",
        "difficulty": "easy",
        "category": "behavioral",
        "hint": "Show end-to-end ownership: schema design, API, frontend, tests, deployment.",
        "sample_answer": "I start with requirements clarification, then design the data schema and API contract (OpenAPI spec). I build the backend endpoint with validation and tests, then wire up the frontend with optimistic updates. I write integration tests, do a code review, and deploy behind a feature flag to canary users before full rollout.",
    },
    {
        "question": "Explain how JWT authentication works and what security considerations you must keep in mind.",
        "job_role": "Full Stack Engineer",
        "difficulty": "medium",
        "category": "technical",
        "hint": "Cover token structure, signing, expiry, refresh tokens, and storage.",
        "sample_answer": "JWTs are signed tokens containing header, payload, and signature (HMAC/RSA). The server verifies the signature without a database lookup. Security considerations: use short expiry (15 min) with refresh tokens, store tokens in HttpOnly cookies (not localStorage) to prevent XSS, validate audience/issuer claims, and rotate signing keys periodically.",
    },
    {
        "question": "Design a multi-tenant SaaS application. How do you isolate tenant data?",
        "job_role": "Full Stack Engineer",
        "difficulty": "hard",
        "category": "system_design",
        "hint": "Compare database-per-tenant, schema-per-tenant, and row-level isolation.",
        "sample_answer": "Three approaches: (1) DB-per-tenant — strongest isolation, highest cost; (2) Schema-per-tenant — good isolation, moderate cost, complex migrations; (3) Row-level with tenant_id — cheapest, easiest to manage, but requires careful query scoping and RLS policies. I'd use row-level isolation with PostgreSQL RLS for a cost-effective SaaS, with per-tenant encryption keys for sensitive fields.",
    },
    {
        "question": "How do you handle CORS and why does it exist?",
        "job_role": "Full Stack Engineer",
        "difficulty": "easy",
        "category": "technical",
        "hint": "Explain same-origin policy, preflight requests, and server-side configuration.",
        "sample_answer": "CORS is a browser security feature that restricts cross-origin HTTP requests based on the same-origin policy. The server signals allowed origins via Access-Control-Allow-Origin headers. For non-simple requests, the browser sends a preflight OPTIONS request. I configure CORS at the API gateway or framework level, whitelisting only trusted origins, never using wildcard '*' for credentialed requests.",
    },

    # ═══════════════════════════════════════════════════════════════
    # DEVOPS ENGINEER
    # ═══════════════════════════════════════════════════════════════
    {
        "question": "Explain the difference between CI and CD. What does a good pipeline look like?",
        "job_role": "DevOps Engineer",
        "difficulty": "easy",
        "category": "technical",
        "hint": "Cover build, test, security scan, and deployment gates.",
        "sample_answer": "CI (Continuous Integration) automatically builds and tests code on every commit. CD (Continuous Delivery/Deployment) extends CI to automatically release to staging or production. A good pipeline includes: lint → unit tests → build → integration tests → SAST/DAST security scan → container scan → deploy to staging → smoke tests → promote to production.",
    },
    {
        "question": "What is Infrastructure as Code (IaC) and why is it important?",
        "job_role": "DevOps Engineer",
        "difficulty": "easy",
        "category": "technical",
        "hint": "Mention reproducibility, version control, drift prevention, and tools.",
        "sample_answer": "IaC means managing infrastructure through machine-readable config files (Terraform, Pulumi, CloudFormation) instead of manual processes. Benefits: version-controlled, reproducible environments; easy rollback; eliminates configuration drift; enables peer review of infrastructure changes; and self-service provisioning for developers.",
    },
    {
        "question": "How would you design a zero-downtime deployment strategy for a stateful application?",
        "job_role": "DevOps Engineer",
        "difficulty": "medium",
        "category": "system_design",
        "hint": "Consider blue-green, canary releases, database migrations, and rollback.",
        "sample_answer": "Use a blue-green deployment: provision an identical green environment, run db migrations that are backward-compatible (expand-contract pattern), shift traffic via load balancer, monitor error rates, and if healthy, decommission blue. For databases, separate schema migrations from code deploys so old code works with the new schema.",
    },
    {
        "question": "Describe a major production incident you handled. How did you approach the post-mortem?",
        "job_role": "DevOps Engineer",
        "difficulty": "hard",
        "category": "behavioral",
        "hint": "Use STAR. Show incident command structure, communication, and blameless culture.",
        "sample_answer": "A misconfigured Terraform change took down our load balancer, causing a 22-minute outage. I was incident commander: I assembled a war room, delegated investigation (network team, app team), and handled stakeholder communication on a 5-minute cadence. We rolled back the change within 15 minutes. The post-mortem was blameless—we added a Terraform plan approval gate and blast-radius tests to prevent recurrence.",
    },
    {
        "question": "Explain Kubernetes pods, deployments, and services. How do they relate?",
        "job_role": "DevOps Engineer",
        "difficulty": "medium",
        "category": "technical",
        "hint": "Cover the abstraction layers and how traffic flows from service to pod.",
        "sample_answer": "A Pod is the smallest deployable unit—one or more containers sharing network/storage. A Deployment manages a desired number of Pod replicas and handles rolling updates and rollbacks. A Service is a stable network endpoint that load-balances traffic across matching Pods using label selectors. Ingress routes external HTTP traffic to Services.",
    },
    {
        "question": "How do you approach secrets management in a cloud-native environment?",
        "job_role": "DevOps Engineer",
        "difficulty": "hard",
        "category": "technical",
        "hint": "Cover tools, dynamic secrets, least privilege, rotation, and audit logging.",
        "sample_answer": "I use HashiCorp Vault or a cloud-native solution (AWS Secrets Manager, GCP Secret Manager). Applications access secrets via short-lived dynamic credentials rather than static secrets. Secrets are never stored in environment variables or source code. I enforce least-privilege IAM policies, enable automatic rotation, and audit all secret access. Kubernetes workloads use the Vault Agent Sidecar or External Secrets Operator.",
    },

    # ═══════════════════════════════════════════════════════════════
    # CLOUD ENGINEER
    # ═══════════════════════════════════════════════════════════════
    {
        "question": "Explain the differences between IaaS, PaaS, and SaaS with examples.",
        "job_role": "Cloud Engineer",
        "difficulty": "easy",
        "category": "technical",
        "hint": "Focus on the responsibility model and typical use cases for each.",
        "sample_answer": "IaaS (e.g., AWS EC2) gives raw VMs—you manage OS, runtime, and app. PaaS (e.g., Heroku, Cloud Run) manages the runtime; you bring only the code. SaaS (e.g., Gmail, Salesforce) is fully managed—you just consume the product. The higher the abstraction, the less you manage but the less control you have.",
    },
    {
        "question": "How do you design a highly available multi-region architecture on AWS?",
        "job_role": "Cloud Engineer",
        "difficulty": "hard",
        "category": "system_design",
        "hint": "Cover Route 53 health checks, RDS Multi-AZ, Global Accelerator, and failover.",
        "sample_answer": "Deploy the application in two regions (primary + DR). Use Route 53 latency or failover routing. Each region has a VPC with public/private subnets, ALB, Auto Scaling Groups, and RDS Multi-AZ. Use Aurora Global Database for cross-region replication with sub-second RPO. CloudFront serves static assets globally. Runbooks and automated failover tests run quarterly.",
    },
    {
        "question": "What is a VPC and how does subnet design work?",
        "job_role": "Cloud Engineer",
        "difficulty": "easy",
        "category": "technical",
        "hint": "Cover public vs private subnets, NAT gateway, route tables, and security groups.",
        "sample_answer": "A VPC is an isolated virtual network in AWS. Public subnets have routes to an Internet Gateway and host load balancers or bastion hosts. Private subnets host application servers and databases with no direct internet access; they use a NAT Gateway for outbound traffic. Security Groups act as instance-level firewalls; NACLs provide subnet-level filtering.",
    },
    {
        "question": "Tell me about a cloud cost optimisation initiative you led.",
        "job_role": "Cloud Engineer",
        "difficulty": "medium",
        "category": "behavioral",
        "hint": "Quantify savings. Mention Reserved Instances, right-sizing, spot instances, or lifecycle policies.",
        "sample_answer": "I audited our AWS costs and found 40% of EC2 spend was on over-provisioned instances running at <10% CPU. I right-sized 60 instances, converted long-running workloads to Reserved Instances, migrated batch jobs to Spot, and added S3 lifecycle policies to Glacier. Monthly bill dropped by $28K—35% savings.",
    },
    {
        "question": "What is serverless computing and what are its limitations?",
        "job_role": "Cloud Engineer",
        "difficulty": "medium",
        "category": "technical",
        "hint": "Cover Lambda/Cloud Functions, cold starts, execution limits, and stateless design.",
        "sample_answer": "Serverless (e.g., AWS Lambda) lets you run code without managing servers. You pay per invocation and execution time. Limitations include cold starts (latency on first invocation), execution time limits (15 min for Lambda), no persistent local state, and vendor lock-in. It works best for event-driven, stateless, short-lived workloads.",
    },

    # ═══════════════════════════════════════════════════════════════
    # DATA ENGINEER
    # ═══════════════════════════════════════════════════════════════
    {
        "question": "Explain the difference between OLTP and OLAP databases. When do you use each?",
        "job_role": "Data Engineer",
        "difficulty": "easy",
        "category": "technical",
        "hint": "Think about workload patterns, normalisation, and row vs column storage.",
        "sample_answer": "OLTP (e.g., PostgreSQL) is optimised for high-concurrency, low-latency transactional reads and writes—row-oriented storage, normalised schema. OLAP (e.g., BigQuery, Redshift) is optimised for complex aggregations over large datasets—columnar storage, denormalised star/snowflake schema. OLTP powers applications; OLAP powers analytics and reporting.",
    },
    {
        "question": "What is an ELT pipeline and how does it differ from ETL?",
        "job_role": "Data Engineer",
        "difficulty": "easy",
        "category": "technical",
        "hint": "Cover the sequencing of transform step and the role of modern data warehouses.",
        "sample_answer": "ETL transforms data before loading it into the target (useful for legacy warehouses with limited compute). ELT loads raw data first, then transforms it inside the warehouse (BigQuery, Snowflake) where compute is cheap and scalable. ELT is preferred in modern data stacks because raw data is preserved for re-transformation and the warehouse handles scale.",
    },
    {
        "question": "How would you design a data pipeline that processes 1 TB of event data daily with exactly-once semantics?",
        "job_role": "Data Engineer",
        "difficulty": "hard",
        "category": "system_design",
        "hint": "Cover Kafka, Flink/Spark, idempotent writes, and checkpointing.",
        "sample_answer": "Use Kafka for event ingestion with producer idempotency enabled. Process with Apache Flink using a stateful streaming job with checkpointing to S3. Write to a data lake (Parquet on S3) via transactional writes (Apache Iceberg/Delta Lake) which provide exactly-once guarantees. A Spark batch job daily reconciles data quality and backfills missing partitions.",
    },
    {
        "question": "Tell me about a data quality issue you discovered and how you resolved it.",
        "job_role": "Data Engineer",
        "difficulty": "medium",
        "category": "behavioral",
        "hint": "Show detection, root cause, fix, and preventive monitoring.",
        "sample_answer": "Our daily revenue dashboard was showing 15% inflation because orders cancelled within 5 minutes were not excluded. I traced the issue to a join condition that missed the cancellation event due to a timing window in our Kafka consumer. I fixed the SQL, backfilled 6 weeks of data, and added a Great Expectations check on net revenue vs gross revenue that alerts within 5 minutes of pipeline completion.",
    },
    {
        "question": "Explain partitioning and clustering in BigQuery. How do they improve query performance?",
        "job_role": "Data Engineer",
        "difficulty": "medium",
        "category": "technical",
        "hint": "Compare partitioning (physical data organisation) vs clustering (sort within partitions).",
        "sample_answer": "Partitioning splits a table into segments (usually by date) so BigQuery only scans relevant partitions, reducing bytes billed. Clustering sorts data within partitions by one or more columns, allowing BigQuery to skip blocks where the cluster key doesn't match the filter. Together they can reduce scan bytes by 90%+ on filtered queries.",
    },

    # ═══════════════════════════════════════════════════════════════
    # DATA SCIENTIST
    # ═══════════════════════════════════════════════════════════════
    {
        "question": "Explain the bias-variance trade-off in machine learning.",
        "job_role": "Data Scientist",
        "difficulty": "easy",
        "category": "technical",
        "hint": "Use a simple analogy and relate it to model complexity.",
        "sample_answer": "High bias means the model is too simple and underfits (misses patterns in training data). High variance means the model is too complex and overfits (memorises noise). The goal is the sweet spot—low bias and low variance. Techniques to reduce variance: regularisation, dropout, cross-validation, ensemble methods. To reduce bias: more features, more complex model.",
    },
    {
        "question": "How do you handle class imbalance in a classification problem?",
        "job_role": "Data Scientist",
        "difficulty": "medium",
        "category": "technical",
        "hint": "Mention resampling, class weights, threshold tuning, and evaluation metrics.",
        "sample_answer": "Options include oversampling the minority class (SMOTE), undersampling the majority class, or using class_weight='balanced' in sklearn. For the model, I use precision-recall AUC or F1 instead of accuracy (which is misleading for imbalanced data). I also tune the decision threshold on a validation set to balance precision and recall based on business requirements.",
    },
    {
        "question": "Describe an end-to-end machine learning project you delivered. What challenges did you face?",
        "job_role": "Data Scientist",
        "difficulty": "hard",
        "category": "behavioral",
        "hint": "Cover problem framing, data, modelling, evaluation, and deployment.",
        "sample_answer": "I built a customer churn predictor for a telecom company. Challenges: 20% missing data (imputed with median and 'missing' flag features), class imbalance (14% churn rate, used SMOTE + threshold tuning), and model drift (added PSI monitoring). Deployed with FastAPI on GCP Cloud Run. The model reduced churn by 8% in the first quarter.",
    },
    {
        "question": "Explain how gradient boosting works and how it differs from random forests.",
        "job_role": "Data Scientist",
        "difficulty": "medium",
        "category": "technical",
        "hint": "Focus on sequential vs parallel ensembles and residual fitting.",
        "sample_answer": "Both use ensembles of decision trees. Random forests train trees in parallel on random subsets and average predictions—reducing variance. Gradient boosting trains trees sequentially; each tree fits the residuals of the previous ensemble. Boosting tends to achieve higher accuracy but is more prone to overfitting and requires careful tuning of learning rate and depth.",
    },
    {
        "question": "Design an A/B testing framework for a recommendation system. What metrics do you track?",
        "job_role": "Data Scientist",
        "difficulty": "hard",
        "category": "system_design",
        "hint": "Cover randomisation, guardrail metrics, sample size, and novelty effects.",
        "sample_answer": "Randomly assign users to control/treatment at the user level (not session, to avoid carryover). Primary metrics: CTR, conversion, revenue. Guardrail metrics: latency, error rate, diversity. Run a power analysis to determine minimum sample size for 80% power at α=0.05. Watch for novelty bias (users clicking new things out of curiosity). Use Welch's t-test for means; chi-squared for proportions. Minimum runtime: 2 weeks to capture weekly seasonality.",
    },

    # ═══════════════════════════════════════════════════════════════
    # ML ENGINEER
    # ═══════════════════════════════════════════════════════════════
    {
        "question": "What is the difference between a data scientist and an ML engineer?",
        "job_role": "ML Engineer",
        "difficulty": "easy",
        "category": "behavioral",
        "hint": "Focus on production concerns, MLOps, and software engineering rigour.",
        "sample_answer": "Data scientists focus on exploration, experimentation, and model accuracy. ML engineers productionise those models: building reliable training pipelines, feature stores, model serving infrastructure, monitoring, and retraining automation. MLE work is closer to software engineering—reliability, scalability, and maintainability matter as much as model quality.",
    },
    {
        "question": "Explain feature stores. Why are they important in production ML?",
        "job_role": "ML Engineer",
        "difficulty": "medium",
        "category": "technical",
        "hint": "Cover training-serving skew, online vs offline stores, and point-in-time correctness.",
        "sample_answer": "Feature stores centralise feature computation and storage. They solve training-serving skew (using different feature logic in training vs inference), provide point-in-time correct lookups for training to prevent leakage, and allow feature reuse across models. Online stores (Redis/DynamoDB) serve low-latency inference; offline stores (Hive/BigQuery) serve training.",
    },
    {
        "question": "Design an ML platform for training and serving 50+ models at scale.",
        "job_role": "ML Engineer",
        "difficulty": "hard",
        "category": "system_design",
        "hint": "Cover training orchestration, model registry, serving, monitoring, and retraining triggers.",
        "sample_answer": "Training: Kubeflow/Metaflow for pipeline orchestration; spot GPU instances for cost savings. Model Registry: MLflow or Vertex AI for versioning and metadata. Serving: Seldon or KServe for model deployment with auto-scaling; canary deploys for safe rollout. Monitoring: track data drift (PSI), concept drift (prediction distribution shift), and business KPIs. Automated retraining triggers when drift exceeds thresholds.",
    },
    {
        "question": "How do you detect and handle model drift in production?",
        "job_role": "ML Engineer",
        "difficulty": "hard",
        "category": "technical",
        "hint": "Differentiate data drift, concept drift, and upstream data pipeline changes.",
        "sample_answer": "Monitor input feature distributions using PSI (Population Stability Index) against a training baseline. Track prediction distribution shift and, where labels are available with delay, model performance (F1, AUC). Set alerting thresholds. On detection, investigate root cause: data pipeline change, world event, or concept drift. If drift is confirmed, trigger retraining with recent data and validate before promoting the new model.",
    },
    {
        "question": "Tell me about a time an ML model you deployed performed poorly in production.",
        "job_role": "ML Engineer",
        "difficulty": "medium",
        "category": "behavioral",
        "hint": "Show post-mortem thinking, monitoring, and model iteration.",
        "sample_answer": "Our fraud detection model saw precision drop from 87% to 61% three months after launch. Investigation revealed that fraudsters had adapted their behaviour (concept drift) and a new payment method was added to production without being included in training data. I retrained with recent labelled data, added the new payment feature, and set up a monthly retraining cron. Precision recovered to 89%.",
    },

    # ═══════════════════════════════════════════════════════════════
    # AI ENGINEER
    # ═══════════════════════════════════════════════════════════════
    {
        "question": "Explain how transformer-based LLMs work at a high level.",
        "job_role": "AI Engineer",
        "difficulty": "easy",
        "category": "technical",
        "hint": "Cover tokenisation, attention mechanism, and autoregressive generation.",
        "sample_answer": "LLMs tokenise input text into subword tokens. The transformer encoder/decoder uses self-attention to compute relationships between all tokens simultaneously, unlike RNNs which process sequentially. During generation, the model autoregressively predicts the next token based on all previous context. Pre-training on large corpora gives broad language understanding; fine-tuning aligns the model to specific tasks or behaviours.",
    },
    {
        "question": "What is RAG (Retrieval-Augmented Generation) and when would you use it?",
        "job_role": "AI Engineer",
        "difficulty": "medium",
        "category": "technical",
        "hint": "Explain the retrieval step, vector databases, and why it complements LLMs.",
        "sample_answer": "RAG supplements an LLM's static knowledge by retrieving relevant documents at inference time. A query is embedded into a vector, top-k similar documents are retrieved from a vector database (Pinecone, Weaviate), and the retrieved context is injected into the prompt. Use RAG when you need up-to-date or domain-specific knowledge that wasn't in the model's training data.",
    },
    {
        "question": "Design an AI-powered customer support system that handles 10,000 queries per day.",
        "job_role": "AI Engineer",
        "difficulty": "hard",
        "category": "system_design",
        "hint": "Cover intent classification, RAG, fallback to humans, cost management, and safety.",
        "sample_answer": "Classify incoming queries (intent detection using a fine-tuned classifier). Route simple FAQ queries to a RAG pipeline over your knowledge base. For complex or sensitive queries, escalate to human agents via a queue. Use GPT-4 for generation with output filtering (harmful content, PII). Cache common query embeddings. Monitor hallucination rate and CSAT. Keep humans in the loop for anything involving payments or account changes.",
    },
    {
        "question": "Tell me about an AI/ML feature you built. How did you evaluate its quality?",
        "job_role": "AI Engineer",
        "difficulty": "medium",
        "category": "behavioral",
        "hint": "Mention both offline (benchmark datasets) and online (A/B test) evaluation.",
        "sample_answer": "I built an AI document summariser for legal contracts. Offline evaluation: ROUGE scores on a human-labelled holdout set and human preference scoring (blind A/B with lawyers). Online evaluation: A/B test measuring time-to-review reduction and lawyer satisfaction ratings. The feature reduced contract review time by 35% in the test group.",
    },
    {
        "question": "What are prompt injection attacks and how do you defend against them?",
        "job_role": "AI Engineer",
        "difficulty": "hard",
        "category": "technical",
        "hint": "Cover direct injection, indirect injection, and mitigation strategies.",
        "sample_answer": "Prompt injection occurs when malicious user input overrides system instructions (e.g., 'Ignore previous instructions and…'). Direct injection is in the user's own input; indirect injection is in retrieved documents (RAG). Mitigations: strict input sanitisation, separate system-prompt from user input, output filtering, using a classifier to detect injection attempts, privilege separation (don't give the LLM access to sensitive actions), and human approval for high-stakes operations.",
    },

    # ═══════════════════════════════════════════════════════════════
    # MOBILE ENGINEER
    # ═══════════════════════════════════════════════════════════════
    {
        "question": "Explain the mobile application lifecycle on Android or iOS.",
        "job_role": "Mobile Engineer",
        "difficulty": "easy",
        "category": "technical",
        "hint": "Cover the key lifecycle states and what each means for resource management.",
        "sample_answer": "On iOS: Not Running → Inactive → Active → Background → Suspended. On Active the app is in foreground; on Background it can execute briefly; Suspended is frozen in memory. On Android: onCreate → onStart → onResume (foreground) → onPause → onStop → onDestroy. Understanding lifecycle is critical for saving state, releasing resources, and handling interruptions like calls.",
    },
    {
        "question": "How do you optimise battery usage in a mobile application?",
        "job_role": "Mobile Engineer",
        "difficulty": "medium",
        "category": "technical",
        "hint": "Cover network batching, location, background processing, and wake locks.",
        "sample_answer": "Batch network requests, use push notifications instead of polling, request location only when needed (significant-change API instead of continuous GPS), use background processing frameworks (WorkManager on Android, BGTaskScheduler on iOS) to defer non-urgent work, avoid holding wake locks unnecessarily, and profile with Xcode Energy Gauge or Android Profiler.",
    },
    {
        "question": "Design an offline-first mobile note-taking application.",
        "job_role": "Mobile Engineer",
        "difficulty": "hard",
        "category": "system_design",
        "hint": "Cover local storage, conflict resolution, sync strategy, and CRDTs.",
        "sample_answer": "Store all notes locally in SQLite (Android Room / Core Data on iOS). On save, write locally and queue a sync operation. Sync uses a last-write-wins or CRDT strategy. Each note gets a vector clock for conflict detection. A background sync job processes the queue when the network is available. The UI always reads from local storage and shows a sync status indicator.",
    },
    {
        "question": "Tell me about a critical bug you fixed in a mobile app. How did you find and resolve it?",
        "job_role": "Mobile Engineer",
        "difficulty": "medium",
        "category": "behavioral",
        "hint": "Show systematic debugging with mobile-specific tools.",
        "sample_answer": "Our iOS app had occasional crashes on launch that appeared in Crashlytics. The stack trace pointed to a nil-optional unwrap in an AppDelegate method. I reproduced it locally by clearing the keychain (auth token was nil on first launch after reinstall). I added a safe guard statement and unit tests for the nil case. Crash rate dropped from 0.4% to 0%.",
    },

    # ═══════════════════════════════════════════════════════════════
    # IOS ENGINEER
    # ═══════════════════════════════════════════════════════════════
    {
        "question": "Explain the difference between value types and reference types in Swift.",
        "job_role": "iOS Engineer",
        "difficulty": "easy",
        "category": "technical",
        "hint": "Cover struct vs class, copy-on-write, and memory implications.",
        "sample_answer": "Structs, enums, and tuples are value types — copied on assignment. Classes are reference types — assignment copies the pointer. Swift uses copy-on-write for collections: they share storage until mutated. Use structs for model data (safer, no retain cycles); use classes for identity-based objects or when inheritance is needed.",
    },
    {
        "question": "What is the difference between Grand Central Dispatch (GCD) and Swift Concurrency (async/await)?",
        "job_role": "iOS Engineer",
        "difficulty": "medium",
        "category": "technical",
        "hint": "Cover thread management, structured concurrency, cancellation, and readability.",
        "sample_answer": "GCD uses completion handlers and DispatchQueues — error-prone, hard to cancel, and leads to callback hell. Swift Concurrency (async/await) provides structured concurrency with Tasks and TaskGroups, automatic cancellation propagation, and actor-based data isolation. Code is linear and readable. Prefer async/await for new code; GCD is still useful for bridging legacy APIs.",
    },
    {
        "question": "Design a SwiftUI architecture for a production iOS app with complex state.",
        "job_role": "iOS Engineer",
        "difficulty": "hard",
        "category": "system_design",
        "hint": "Compare MVVM, TCA (The Composable Architecture), and Redux patterns.",
        "sample_answer": "I use MVVM with SwiftUI's @StateObject/@ObservableObject for local state and a shared AppState + @EnvironmentObject for global state, injected via the SwiftUI environment. For complex apps I adopt TCA: reducers handle state mutations deterministically, effects handle side effects (network, persistence), which makes testing and debugging straightforward. All business logic is in reducers — fully unit-testable without UI.",
    },

    # ═══════════════════════════════════════════════════════════════
    # ANDROID ENGINEER
    # ═══════════════════════════════════════════════════════════════
    {
        "question": "Explain Jetpack Compose vs the traditional View system in Android.",
        "job_role": "Android Engineer",
        "difficulty": "easy",
        "category": "technical",
        "hint": "Compare declarative vs imperative UI, recomposition, and migration path.",
        "sample_answer": "The View system is imperative — you manipulate views directly (findViewById, setText). Jetpack Compose is declarative — you describe the UI as a function of state; when state changes, Compose recomposes only affected composables. Compose eliminates XML layouts, simplifies animations, and has better tooling (Compose Preview). It's the recommended approach for new Android development.",
    },
    {
        "question": "How does ViewModel survive configuration changes in Android?",
        "job_role": "Android Engineer",
        "difficulty": "medium",
        "category": "technical",
        "hint": "Cover the ViewModelStore and what is recreated vs retained on rotation.",
        "sample_answer": "When a configuration change (rotation) occurs, the Activity is destroyed and recreated. The ViewModelStore is attached to the non-configuration instance (retained by the system), so the ViewModel is not destroyed. The new Activity instance retrieves the same ViewModel via ViewModelProvider. State stored in the ViewModel persists; UI state in the view hierarchy does not.",
    },
    {
        "question": "Design the offline-first architecture for an Android social media app.",
        "job_role": "Android Engineer",
        "difficulty": "hard",
        "category": "system_design",
        "hint": "Cover Room, WorkManager, Repository pattern, and conflict handling.",
        "sample_answer": "Use Room as the single source of truth. Repository layer reads from Room and serves data immediately; a background sync layer fetches from the network and writes to Room, which triggers UI updates via Flow. Pending writes (new posts, likes) are stored in a pending_operations table. WorkManager handles sync with retry and backoff. Conflicts are resolved with server-wins or last-write-wins depending on the entity.",
    },

    # ═══════════════════════════════════════════════════════════════
    # QA ENGINEER
    # ═══════════════════════════════════════════════════════════════
    {
        "question": "Explain the difference between functional and non-functional testing.",
        "job_role": "QA Engineer",
        "difficulty": "easy",
        "category": "technical",
        "hint": "List types of non-functional testing with examples.",
        "sample_answer": "Functional testing verifies that the system does what it's supposed to — unit, integration, regression, smoke, and UAT tests. Non-functional testing checks how well it does it — performance, load, security, usability, and accessibility testing. Both are essential; functional tests catch bugs, non-functional tests catch degraded quality.",
    },
    {
        "question": "How do you approach creating a test strategy for a new product?",
        "job_role": "QA Engineer",
        "difficulty": "medium",
        "category": "behavioral",
        "hint": "Cover risk analysis, test pyramid, environments, and entry/exit criteria.",
        "sample_answer": "I start with a risk assessment (what would hurt most if broken?) and use that to prioritise test coverage. I design a test pyramid: many unit tests, some integration tests, few E2E tests. I define test environments (dev, staging, prod-like), data strategy, entry/exit criteria, and a defect management process. I involve developers early so they write unit tests from the start.",
    },
    {
        "question": "How would you design an automated testing framework for a complex web application?",
        "job_role": "QA Engineer",
        "difficulty": "hard",
        "category": "system_design",
        "hint": "Cover tool choice, Page Object Model, CI integration, reporting, and flakiness management.",
        "sample_answer": "I'd use Playwright (cross-browser, fast, reliable) with TypeScript. The framework uses the Page Object Model to encapsulate UI interactions. Tests run in CI on every PR with parallel execution across browsers. Failed tests retry once to detect genuine failures vs flakiness. Allure generates test reports with screenshots on failure. A dedicated 'flaky test' label tracks and prioritises elimination of unstable tests.",
    },
    {
        "question": "Explain the concept of shift-left testing.",
        "job_role": "QA Engineer",
        "difficulty": "easy",
        "category": "technical",
        "hint": "Describe when testing starts, who is involved, and why it reduces cost.",
        "sample_answer": "Shift-left means moving testing earlier in the SDLC — starting with requirements review, involving QA in story grooming, writing acceptance criteria before coding, and having developers write unit tests alongside features. Defects found in requirements or design are 10-100x cheaper to fix than defects found in production.",
    },

    # ═══════════════════════════════════════════════════════════════
    # SDET
    # ═══════════════════════════════════════════════════════════════
    {
        "question": "What is the difference between white-box and black-box testing?",
        "job_role": "SDET",
        "difficulty": "easy",
        "category": "technical",
        "hint": "Focus on tester's knowledge of internals and test design techniques.",
        "sample_answer": "Black-box testing treats the system as opaque — testers know only inputs and expected outputs (based on requirements). White-box (glass-box) testing uses knowledge of internals to design test cases covering code paths, branches, and conditions. SDETs typically use both: black-box for integration and API tests, white-box for unit and mutation tests.",
    },
    {
        "question": "How do you test a REST API systematically? What are the key test areas?",
        "job_role": "SDET",
        "difficulty": "medium",
        "category": "technical",
        "hint": "Cover functional, contract, security, performance, and error-handling tests.",
        "sample_answer": "Key areas: (1) Happy path — valid inputs return expected responses. (2) Contract testing — schema validation with every release. (3) Boundary/negative tests — invalid inputs, missing fields, type mismatches, large payloads. (4) Auth/authz — unauthenticated and unauthorised requests. (5) Rate limiting — verify 429 responses. (6) Performance — latency under load. Tools: Postman, Newman, REST Assured, Karate.",
    },
    {
        "question": "Design a CI/CD quality gate that ensures code quality before production deployment.",
        "job_role": "SDET",
        "difficulty": "hard",
        "category": "system_design",
        "hint": "Cover linting, unit tests, code coverage, SAST, API tests, and smoke tests.",
        "sample_answer": "Gate 1 (pre-merge): lint, unit tests, code coverage ≥80%, SAST (Semgrep/SonarQube). Gate 2 (post-merge, pre-staging): API integration tests, contract tests, dependency vulnerability scan. Gate 3 (staging): E2E smoke tests, performance baseline tests. Gate 4 (pre-prod): canary release with SLO monitoring. Any gate failure blocks promotion. Test results and coverage trends are published to a dashboard.",
    },

    # ═══════════════════════════════════════════════════════════════
    # SECURITY ENGINEER
    # ═══════════════════════════════════════════════════════════════
    {
        "question": "Explain the OWASP Top 10 and the three you consider most critical.",
        "job_role": "Security Engineer",
        "difficulty": "easy",
        "category": "technical",
        "hint": "Mention Injection, Broken Auth, and Insecure Design at minimum.",
        "sample_answer": "The OWASP Top 10 covers the most critical web application security risks. I consider most critical: (1) Injection (SQL, command) — can lead to full data breach; (2) Broken Authentication — poor session management enables account takeover; (3) Cryptographic Failures — sensitive data exposed in transit or at rest. All three directly lead to data breaches with regulatory and reputational consequences.",
    },
    {
        "question": "How does SQL injection work and how do you prevent it?",
        "job_role": "Security Engineer",
        "difficulty": "easy",
        "category": "technical",
        "hint": "Cover parameterised queries, ORMs, input validation, and WAFs.",
        "sample_answer": "SQL injection occurs when user input is concatenated directly into a query string, allowing the attacker to alter the query's logic or extract data. Prevention: always use parameterised queries or prepared statements; use ORM frameworks that handle escaping; validate and whitelist inputs; deploy a WAF as a secondary defence; apply the principle of least privilege to database users.",
    },
    {
        "question": "Design a secrets management and rotation strategy for a cloud-native application.",
        "job_role": "Security Engineer",
        "difficulty": "hard",
        "category": "system_design",
        "hint": "Cover Vault, KMS, rotation automation, and audit logging.",
        "sample_answer": "Centralise all secrets in HashiCorp Vault or AWS Secrets Manager. Applications authenticate using short-lived tokens (Vault AppRole or AWS IAM role) to retrieve secrets at start-up or renewal. Automate rotation using Vault's database secrets engine (generates a new DB credential on rotation). Log every secret access to an immutable audit log. Alert on access from unexpected sources. Never store secrets in environment variables in CI logs.",
    },
    {
        "question": "Tell me about a security vulnerability you discovered and remediated.",
        "job_role": "Security Engineer",
        "difficulty": "medium",
        "category": "behavioral",
        "hint": "Show identification, severity assessment, fix, and prevention process.",
        "sample_answer": "During a routine SAST scan I found an IDOR (Insecure Direct Object Reference) vulnerability: a user could access other users' invoices by changing the ID in the URL. I rated it Critical (CVSS 8.1), immediately hot-fixed with object-level authorisation checks (verify the requested resource belongs to the authenticated user), added regression tests, and updated our secure-coding guidelines and code review checklist.",
    },
    {
        "question": "Explain the difference between authentication and authorisation. What common mistakes do developers make?",
        "job_role": "Security Engineer",
        "difficulty": "medium",
        "category": "technical",
        "hint": "Cover AuthN vs AuthZ, common mistakes like trusting client-side data, and RBAC.",
        "sample_answer": "Authentication (AuthN) verifies identity — who are you? Authorisation (AuthZ) verifies permissions — what can you do? Common mistakes: (1) Checking AuthN but skipping AuthZ on sensitive endpoints; (2) Trusting client-provided user_id or role claims without server-side verification; (3) Not enforcing AuthZ at the object level (IDOR); (4) Using JWT secret 'none' algorithm; (5) Not expiring sessions on logout.",
    },

    # ═══════════════════════════════════════════════════════════════
    # SITE RELIABILITY ENGINEER
    # ═══════════════════════════════════════════════════════════════
    {
        "question": "What are SLIs, SLOs, and SLAs? How do they relate to error budgets?",
        "job_role": "Site Reliability Engineer",
        "difficulty": "easy",
        "category": "technical",
        "hint": "Explain each term and how error budgets enable innovation vs reliability balance.",
        "sample_answer": "SLI (Service Level Indicator) is a metric measuring service behaviour (e.g., request success rate). SLO (Service Level Objective) is the target for that metric (e.g., 99.9% success over 30 days). SLA is the contractual commitment with consequences for breach. Error budget = 100% - SLO = the allowed failure budget. If the error budget is exhausted, reliability work takes priority over feature development.",
    },
    {
        "question": "Explain the four golden signals of monitoring.",
        "job_role": "Site Reliability Engineer",
        "difficulty": "easy",
        "category": "technical",
        "hint": "Latency, traffic, errors, saturation — explain each briefly.",
        "sample_answer": "The four golden signals (from the SRE Book): (1) Latency — how long requests take (p50, p99); (2) Traffic — request rate (RPS); (3) Errors — rate of failed requests (5xx, timeouts); (4) Saturation — how 'full' the service is (CPU, memory, queue depth). Monitoring all four gives a complete picture of service health.",
    },
    {
        "question": "Design a multi-region observability stack for a microservices application.",
        "job_role": "Site Reliability Engineer",
        "difficulty": "hard",
        "category": "system_design",
        "hint": "Cover metrics, logs, traces, and alerting with global aggregation.",
        "sample_answer": "Metrics: Prometheus per region, federated into Thanos (global query layer) with long-term storage in object storage. Logs: Fluentd/Fluentbit → GCS/S3 → BigQuery for querying; Loki for recent logs in Grafana. Traces: OpenTelemetry SDK → Tempo or Jaeger. Alerting: region-level alerts for fast detection; global aggregation for SLO burn-rate alerts. Grafana as the unified dashboard layer across regions.",
    },
    {
        "question": "How do you approach on-call and incident management?",
        "job_role": "Site Reliability Engineer",
        "difficulty": "medium",
        "category": "behavioral",
        "hint": "Cover alert hygiene, runbooks, escalation paths, and blameless post-mortems.",
        "sample_answer": "Good on-call starts before incidents: alert on symptoms (not causes), keep alert volume low (100% actionable), write runbooks for every alert. During incidents: declare severity quickly, assign incident commander, communicate status every 15 minutes internally. Post-incident: blameless post-mortem within 48 hours, 5 Whys root-cause analysis, action items tracked to completion, share learnings across teams.",
    },

    # ═══════════════════════════════════════════════════════════════
    # PLATFORM ENGINEER
    # ═══════════════════════════════════════════════════════════════
    {
        "question": "What is an Internal Developer Platform (IDP) and what problems does it solve?",
        "job_role": "Platform Engineer",
        "difficulty": "easy",
        "category": "technical",
        "hint": "Focus on developer experience, cognitive load, and golden paths.",
        "sample_answer": "An IDP is a self-service layer on top of infrastructure that lets developers provision environments, deploy services, and manage dependencies without deep ops knowledge. It reduces cognitive load by providing 'golden paths' (opinionated, pre-approved workflows) for common tasks like creating a new service, running CI, or provisioning a database. Backstage is a popular open-source IDP framework.",
    },
    {
        "question": "Design a self-service infrastructure provisioning platform for 200 developers.",
        "job_role": "Platform Engineer",
        "difficulty": "hard",
        "category": "system_design",
        "hint": "Cover service catalogue, IaC templates, GitOps, guardrails, and cost visibility.",
        "sample_answer": "Build on Backstage for the service catalogue. Infrastructure is defined as Terraform modules in a central repository. Developers fill a form (service name, region, size tier) which generates a PR with parameterised Terraform. Atlantis applies the plan on merge (GitOps). Policy-as-code (OPA/Sentinel) enforces guardrails (no public S3 buckets, required tags for cost attribution). Infracost shows estimated cost before merge. All resources tagged by team for showback.",
    },
    {
        "question": "How do you balance platform standardisation with team autonomy?",
        "job_role": "Platform Engineer",
        "difficulty": "medium",
        "category": "behavioral",
        "hint": "Talk about golden paths, escape hatches, and platform as a product.",
        "sample_answer": "I treat the platform as a product: golden paths for common use cases (80%), escape hatches for teams with legitimate special requirements (20%). I engage with application teams regularly to understand friction, incorporate feedback into platform roadmaps, and measure adoption. I avoid mandating platform use — teams adopt it because it's genuinely better, not because they're forced. Good DX is the best enforcement mechanism.",
    },

    # ═══════════════════════════════════════════════════════════════
    # EMBEDDED ENGINEER
    # ═══════════════════════════════════════════════════════════════
    {
        "question": "Explain the difference between microcontrollers and microprocessors.",
        "job_role": "Embedded Engineer",
        "difficulty": "easy",
        "category": "technical",
        "hint": "Cover integrated peripherals, memory, power consumption, and use cases.",
        "sample_answer": "Microcontrollers (MCU) integrate CPU, RAM, flash, and peripherals (GPIO, ADC, UART) on a single chip — ideal for low-power, cost-sensitive embedded systems. Microprocessors (MPU) are higher-performance CPUs requiring external RAM, storage, and peripherals — used in embedded Linux systems (Raspberry Pi, industrial HMIs). MCUs for simple sensors and actuators; MPUs for complex applications needing an OS.",
    },
    {
        "question": "What is an RTOS and when would you use one?",
        "job_role": "Embedded Engineer",
        "difficulty": "medium",
        "category": "technical",
        "hint": "Cover real-time constraints, task scheduling, determinism, and examples.",
        "sample_answer": "An RTOS provides deterministic, preemptive task scheduling with guaranteed response times. Use it when the system must respond to events within a hard deadline (e.g., motor control, safety systems). Common RTOSes: FreeRTOS, Zephyr, VxWorks. Without an RTOS, complex interrupt-driven super-loops become unmanageable and response times unpredictable.",
    },
    {
        "question": "How do you debug a hard-fault on an ARM Cortex-M microcontroller?",
        "job_role": "Embedded Engineer",
        "difficulty": "hard",
        "category": "technical",
        "hint": "Cover fault status registers, stack unwinding, JTAG/SWD, and common causes.",
        "sample_answer": "First, read the HardFault Status Register (HFSR) and CFSR to identify the fault type (bus fault, usage fault, memory management fault). Hook the HardFault handler to print the stacked registers (LR, PC, PSR). Unwind the stack to find the faulting instruction. Common causes: null pointer dereference, stack overflow, unaligned access, calling code with wrong FPU settings. Use JTAG/SWD with gdb for live inspection.",
    },

    # ═══════════════════════════════════════════════════════════════
    # DATABASE ADMINISTRATOR
    # ═══════════════════════════════════════════════════════════════
    {
        "question": "Explain the ACID properties in databases.",
        "job_role": "Database Administrator",
        "difficulty": "easy",
        "category": "technical",
        "hint": "Define each property and why it matters for data integrity.",
        "sample_answer": "ACID stands for: Atomicity (a transaction is all-or-nothing), Consistency (a transaction brings the db from one valid state to another), Isolation (concurrent transactions don't interfere, controlled by isolation levels), Durability (committed transactions survive crashes, guaranteed by WAL). Together they ensure reliable transaction processing.",
    },
    {
        "question": "How do you approach a slow database and identify the bottleneck?",
        "job_role": "Database Administrator",
        "difficulty": "medium",
        "category": "technical",
        "hint": "Cover pg_stat_activity, slow query log, EXPLAIN ANALYZE, and wait events.",
        "sample_answer": "I start with pg_stat_activity to find long-running queries and lock contention. Enable the slow query log (log_min_duration_statement) to capture offenders. Run EXPLAIN (ANALYZE, BUFFERS) on the problematic query to identify sequential scans, bad estimates, or sort spills. Check pg_stat_user_tables for bloat. Common fixes: add an index, run VACUUM ANALYZE, adjust work_mem, or rewrite the query.",
    },
    {
        "question": "Design a high-availability PostgreSQL setup with zero-data-loss failover.",
        "job_role": "Database Administrator",
        "difficulty": "hard",
        "category": "system_design",
        "hint": "Cover streaming replication, synchronous commit, Patroni, and pgBouncer.",
        "sample_answer": "Primary runs with synchronous_commit=on and one synchronous standby (eliminates data loss on failover). Use Patroni + etcd for automatic leader election and failover. Promote the synchronous standby on primary failure (<30s). pgBouncer in front of Patroni provides connection pooling and transparent failover for applications. Periodic PITR backups to S3 with WAL archiving for point-in-time recovery.",
    },
    {
        "question": "Tell me about a database incident you handled. How did you recover?",
        "job_role": "Database Administrator",
        "difficulty": "hard",
        "category": "behavioral",
        "hint": "Show blameless analysis, recovery steps, and prevention measures.",
        "sample_answer": "A developer accidentally truncated a production table with 500K rows. I immediately paused all writes, identified the exact LSN of the truncation from pg_wal, and performed point-in-time recovery to 5 seconds before the event using WAL archives. Recovery took 45 minutes. Post-mortem: added a TRUNCATE privilege restriction (only DBAs can truncate), and implemented soft-delete (is_deleted flag) as a safety net.",
    },

    # ═══════════════════════════════════════════════════════════════
    # NETWORK ENGINEER
    # ═══════════════════════════════════════════════════════════════
    {
        "question": "Explain the OSI model and which layers are most relevant to a network engineer.",
        "job_role": "Network Engineer",
        "difficulty": "easy",
        "category": "technical",
        "hint": "Briefly describe all 7 layers and focus on where networking problems occur.",
        "sample_answer": "The OSI model has 7 layers: Physical, Data Link, Network, Transport, Session, Presentation, Application. Network engineers work most in Layer 1 (cabling, transceivers), Layer 2 (switching, VLANs, STP), Layer 3 (routing, BGP/OSPF, IP addressing), and Layer 4 (TCP/UDP, firewalls, load balancers). Troubleshooting starts at Layer 1 and works up.",
    },
    {
        "question": "Explain BGP and when you would use it over OSPF.",
        "job_role": "Network Engineer",
        "difficulty": "medium",
        "category": "technical",
        "hint": "Compare path-vector vs link-state, use cases, and scale.",
        "sample_answer": "BGP (Border Gateway Protocol) is a path-vector protocol used for routing between autonomous systems (the internet). OSPF is a link-state protocol used within an AS for fast convergence. Use OSPF for internal datacenter routing (fast convergence, simple config). Use BGP when connecting to multiple ISPs (multi-homing), between datacenters (eBGP), or for policy-based traffic engineering. BGP scales to internet size; OSPF is simpler for internal use.",
    },
    {
        "question": "How would you design a redundant network architecture for a datacenter?",
        "job_role": "Network Engineer",
        "difficulty": "hard",
        "category": "system_design",
        "hint": "Cover spine-leaf topology, ECMP, redundant uplinks, and BFD.",
        "sample_answer": "Use a spine-leaf (Clos) topology for predictable, low-latency east-west traffic. Each leaf switch connects to every spine (no direct leaf-to-leaf links). Use ECMP for load balancing across multiple uplinks. All links are active (no STP blocking). BFD for fast failure detection. Redundant power and dual-homed servers (LACP bonding). External connectivity via BGP to two ISPs (AS-path prepend for traffic steering).",
    },

    # ═══════════════════════════════════════════════════════════════
    # SOLUTIONS ARCHITECT
    # ═══════════════════════════════════════════════════════════════
    {
        "question": "How do you approach a greenfield architecture design for a new product?",
        "job_role": "Solutions Architect",
        "difficulty": "easy",
        "category": "behavioral",
        "hint": "Show requirement gathering, trade-off analysis, and documentation.",
        "sample_answer": "I start with requirements: functional (what it must do), non-functional (scale, latency, availability, compliance), and constraints (team size, budget, timeline). I draw a context diagram, then a component diagram. I evaluate build vs buy for each component, document trade-offs in an ADR (Architecture Decision Record), and review with the team. I design for today's requirements but leave clear seams for future scaling.",
    },
    {
        "question": "When would you choose microservices over a monolith architecture?",
        "job_role": "Solutions Architect",
        "difficulty": "medium",
        "category": "technical",
        "hint": "Discuss team size, deployment independence, operational complexity, and the Strangler Fig.",
        "sample_answer": "Start with a monolith: faster to build, easier to debug, lower operational overhead. Move to microservices when: independent deployability of components is needed, teams are large enough to own separate services (Conway's Law), different components have different scaling requirements, or a component needs a different technology stack. Use the Strangler Fig pattern for gradual extraction. Microservices add operational complexity — only worth it when monolith pain is real.",
    },
    {
        "question": "Design a secure, scalable e-commerce platform handling 100K concurrent users.",
        "job_role": "Solutions Architect",
        "difficulty": "hard",
        "category": "system_design",
        "hint": "Cover CDN, API gateway, microservices, databases, payments, and security.",
        "sample_answer": "CDN (CloudFront) for static assets. API Gateway for routing, auth, and rate limiting. Core services: Product (PostgreSQL + Elasticsearch), Order, Inventory, Payment (PCI-DSS compliant, tokenised). Event-driven with Kafka for order → inventory → fulfillment flow. Redis for sessions and cart. Kubernetes with auto-scaling. WAF + DDoS protection at the edge. Multi-AZ RDS with read replicas. PII encrypted at rest with KMS.",
    },

    # ═══════════════════════════════════════════════════════════════
    # ENGINEERING MANAGER
    # ═══════════════════════════════════════════════════════════════
    {
        "question": "How do you handle a consistent underperformer on your team?",
        "job_role": "Engineering Manager",
        "difficulty": "hard",
        "category": "behavioral",
        "hint": "Show empathy, clear expectations, documented feedback, and decisive action.",
        "sample_answer": "First I investigate root cause — skill gap, motivation, personal issues, or wrong role. I have a direct 1:1 conversation, clearly define expectations and a 30/60/90-day PIP with measurable milestones. I check in weekly, provide coaching, and remove blockers. If performance doesn't improve after genuine support, I escalate through HR processes. Being fair requires being honest and decisive.",
    },
    {
        "question": "How do you balance technical debt reduction with delivering new features?",
        "job_role": "Engineering Manager",
        "difficulty": "medium",
        "category": "behavioral",
        "hint": "Show stakeholder communication, metrics, and budgeting strategies.",
        "sample_answer": "I make tech debt visible by tracking it with business impact (e.g., 'this adds 2 days to every feature in this area'). I negotiate 20% capacity per sprint for debt, bundle refactors with adjacent features, and present debt reduction as risk reduction to business stakeholders. I use metrics like cycle time and DORA metrics to show the ROI of paying down debt.",
    },
    {
        "question": "Walk me through how you run effective 1:1s with your engineers.",
        "job_role": "Engineering Manager",
        "difficulty": "easy",
        "category": "behavioral",
        "hint": "Cover agenda ownership, growth focus, and psychological safety.",
        "sample_answer": "The engineer owns the agenda — 1:1s are for them, not status updates. I send a shared doc beforehand for both of us to add topics. I focus on career growth, blockers, feedback, and wellbeing. I ask open questions ('What's frustrating you?', 'What would you like to learn?'). I take notes and follow through on action items. Consistent, predictable 1:1s build the trust that makes hard conversations easier.",
    },
    {
        "question": "How do you hire effectively and build a high-performing engineering team?",
        "job_role": "Engineering Manager",
        "difficulty": "hard",
        "category": "behavioral",
        "hint": "Cover structured interviews, calibration, diversity, onboarding, and culture.",
        "sample_answer": "I define a clear role scorecard before opening the req. Interviews are structured with consistent questions and a rubric to reduce bias. I include a diverse interview panel. After interviews, we calibrate blind (share scores before discussion). I invest in onboarding — 30/60/90 plan, a buddy, and early wins. I'm transparent about team working norms and psychological safety expectations from day one.",
    },

    # ═══════════════════════════════════════════════════════════════
    # TECHNICAL LEAD
    # ═══════════════════════════════════════════════════════════════
    {
        "question": "How do you onboard a new engineer to your team effectively?",
        "job_role": "Technical Lead",
        "difficulty": "easy",
        "category": "behavioral",
        "hint": "Cover documentation, pairing, early tasks, and feedback loops.",
        "sample_answer": "I prepare before they start: update README, ensure local setup scripts work, write a 30/60/90 plan. Week 1: set up environment and work on a well-scoped 'starter' ticket. I pair with them on the first PR and give detailed code review feedback. Weekly check-ins to surface confusion early. By day 90, they should feel confident shipping independently.",
    },
    {
        "question": "How do you make architectural decisions as a tech lead and get buy-in from your team?",
        "job_role": "Technical Lead",
        "difficulty": "medium",
        "category": "behavioral",
        "hint": "Talk about RFCs, inclusive design sessions, and documenting trade-offs.",
        "sample_answer": "I write an RFC (Request for Comments) documenting the problem, constraints, considered options, and my recommendation with trade-offs. I circulate it to the team for async feedback before a synchronous discussion. I explicitly invite dissenting views. If the team has strong objections, I update the proposal or hold a structured debate. Final decision and rationale are recorded in an ADR.",
    },
    {
        "question": "How do you maintain code quality standards across a team without becoming a bottleneck?",
        "job_role": "Technical Lead",
        "difficulty": "medium",
        "category": "technical",
        "hint": "Mention linting, automated checks, code review norms, pairing, and guild culture.",
        "sample_answer": "Automate what can be automated: linting, formatting, test coverage gates in CI. Document team coding standards in a living guide. Define code review norms (what requires discussion vs merge-on-approval). Pair program on complex features to transfer standards. Run a monthly engineering guild to discuss standards evolution. My goal is to make the 'right' thing the 'easy' thing.",
    },

    # ═══════════════════════════════════════════════════════════════
    # PRODUCT MANAGER
    # ═══════════════════════════════════════════════════════════════
    {
        "question": "How do you prioritise a product backlog when everything seems equally important?",
        "job_role": "Product Manager",
        "difficulty": "medium",
        "category": "behavioral",
        "hint": "Mention frameworks like RICE, ICE, or Kano and how you use data.",
        "sample_answer": "I use the RICE scoring model: Reach × Impact × Confidence ÷ Effort. This quantifies trade-offs and removes gut-feel debates. I validate Reach and Impact with data (user analytics, NPS surveys, support tickets). I then share the ranked list with stakeholders to calibrate and sanity-check. Priorities change when new data arrives — I keep the backlog a living document.",
    },
    {
        "question": "Tell me about a product you built from zero to launch. What was your process?",
        "job_role": "Product Manager",
        "difficulty": "hard",
        "category": "behavioral",
        "hint": "Cover discovery, definition, development, and launch with metrics.",
        "sample_answer": "I led the launch of a mobile payments feature. Discovery: 20 user interviews, competitive analysis, defined the problem statement. Definition: wrote PRD with acceptance criteria and success KPIs (adoption rate, transaction volume). Development: weekly demos, ruthless scope negotiation with engineering. Launch: phased rollout (10% → 50% → 100%), real-time dashboard, support runbook ready. Result: 34% of MAUs adopted within 60 days.",
    },
    {
        "question": "How do you work effectively with engineering teams to deliver a product on time?",
        "job_role": "Product Manager",
        "difficulty": "easy",
        "category": "behavioral",
        "hint": "Emphasise clarity, trust, async communication, and scope management.",
        "sample_answer": "I involve engineers in discovery early so they understand the 'why'. I write clear, testable acceptance criteria. I'm available during development to clarify requirements quickly (hours, not days). I don't change scope mid-sprint without explicit trade-off discussion. I celebrate team wins publicly and shield engineers from unnecessary stakeholder interruption.",
    },
    {
        "question": "Design a product metrics framework for a B2B SaaS application.",
        "job_role": "Product Manager",
        "difficulty": "hard",
        "category": "system_design",
        "hint": "Cover North Star metric, input metrics, guardrail metrics, and instrumentation.",
        "sample_answer": "North Star: Weekly Active Accounts (engagement proxy). Input metrics: activation rate (account set up ≥3 key workflows), feature adoption, NPS, expansion MRR. Guardrail metrics: churn rate, support ticket volume, API error rate. Instrument every user action via a data layer (Segment → BigQuery). Build a self-serve dashboard in Looker. Review metrics weekly with the team and monthly with leadership.",
    },

    # ═══════════════════════════════════════════════════════════════
    # TECHNICAL PROGRAM MANAGER
    # ═══════════════════════════════════════════════════════════════
    {
        "question": "How do you manage dependencies and risks across multiple engineering teams?",
        "job_role": "Technical Program Manager",
        "difficulty": "medium",
        "category": "behavioral",
        "hint": "Cover dependency mapping, RAID log, escalation, and buffer planning.",
        "sample_answer": "At programme start, I map all inter-team dependencies in a RAID log (Risks, Assumptions, Issues, Dependencies). I conduct weekly dependency reviews and surface blockers 2 weeks before they become critical. I maintain a risk register with likelihood/impact scoring and mitigation plans. I escalate early and with solutions, not just problems. Schedule buffers (10-15%) protect against integration surprises.",
    },
    {
        "question": "Tell me about a programme that was off-track. How did you get it back on schedule?",
        "job_role": "Technical Program Manager",
        "difficulty": "hard",
        "category": "behavioral",
        "hint": "Show diagnosis, recovery plan, stakeholder communication, and outcome.",
        "sample_answer": "A platform migration programme was 6 weeks behind with 3 months to go. I audited causes: scope creep (30% more work added), a team under-staffed by two engineers, and testing left to the end. I re-baselined the schedule, cut non-critical scope (deferred 20% to Phase 2), worked with leadership to unblock hiring, and shifted to continuous testing. We delivered on time with 95% of original scope.",
    },
    {
        "question": "How do you communicate programme status to executive stakeholders?",
        "job_role": "Technical Program Manager",
        "difficulty": "easy",
        "category": "behavioral",
        "hint": "Cover structure (RAG status), brevity, and anticipating questions.",
        "sample_answer": "I use a weekly one-pager: RAG status, % complete, key milestones this week, risks/blockers requiring exec attention, decisions needed. Executives read it in 2 minutes. I lead with what they care about: are we on track? If not, what's the plan? I never surface a problem without a proposed solution. I send it Friday afternoon and hold a 15-minute sync Monday for questions.",
    },

    # ═══════════════════════════════════════════════════════════════
    # UI/UX DESIGNER
    # ═══════════════════════════════════════════════════════════════
    {
        "question": "Walk me through your design process from brief to final delivery.",
        "job_role": "UI/UX Designer",
        "difficulty": "easy",
        "category": "behavioral",
        "hint": "Cover discovery, research, ideation, prototyping, testing, and handoff.",
        "sample_answer": "I start with a discovery phase: brief review, stakeholder interviews, and competitive analysis. Research: user interviews and analytics review to identify pain points. Ideation: sketches and information architecture. Prototyping: Figma wireframes → high-fidelity interactive prototypes. Testing: usability testing with 5-8 target users, two rounds. Handoff: annotated Figma spec, design tokens, and an asset library for developers.",
    },
    {
        "question": "How do you advocate for UX in an organisation that prioritises engineering speed?",
        "job_role": "UI/UX Designer",
        "difficulty": "medium",
        "category": "behavioral",
        "hint": "Use data, business impact arguments, and demonstrate ROI of good UX.",
        "sample_answer": "I translate UX problems into business language: 'This confusing checkout flow caused 18% drop-off, costing an estimated $2M annually.' I run quick guerrilla tests (5 users, 2 hours) to generate fast evidence. I join sprint planning to flag UX concerns early before code is written. I celebrate wins publicly — when UX improvements correlate with metric improvements, leadership notices.",
    },
    {
        "question": "Design a mobile onboarding experience for a fintech application. What are your key principles?",
        "job_role": "UI/UX Designer",
        "difficulty": "hard",
        "category": "system_design",
        "hint": "Cover progressive disclosure, trust signals, friction reduction, and accessibility.",
        "sample_answer": "Key principles: (1) Progressive disclosure — reveal information as needed, not all at once. (2) Trust signals — show security certifications, privacy commitments early. (3) Minimum viable friction — ask for only what's needed at each step; defer optional info (profile photo) post-onboarding. (4) Progress indicators — show where users are in the journey. (5) Clear error messages — form validation with actionable feedback. (6) WCAG AA accessibility throughout.",
    },

    # ═══════════════════════════════════════════════════════════════
    # BUSINESS ANALYST
    # ═══════════════════════════════════════════════════════════════
    {
        "question": "How do you elicit requirements from stakeholders who aren't sure what they want?",
        "job_role": "Business Analyst",
        "difficulty": "medium",
        "category": "behavioral",
        "hint": "Cover facilitation techniques, prototyping, and iterative refinement.",
        "sample_answer": "I use facilitated workshops with structured techniques: 'As-Is' vs 'To-Be' process mapping, user story mapping, and dot-voting for priorities. When stakeholders struggle to articulate, I show a rough prototype or competitor example to trigger concrete feedback ('like this, but not that'). I document and reflect back requirements after each session for validation. Iteration is expected — ambiguity reduces with each cycle.",
    },
    {
        "question": "What is the difference between functional and non-functional requirements? Give examples.",
        "job_role": "Business Analyst",
        "difficulty": "easy",
        "category": "technical",
        "hint": "Use real examples from a web application context.",
        "sample_answer": "Functional requirements describe what the system does: 'The user shall be able to reset their password via email.' Non-functional requirements describe quality attributes: 'The system shall handle 10,000 concurrent users with <500ms response time' (performance), 'User passwords shall be stored as bcrypt hashes' (security), 'The UI shall be WCAG AA compliant' (accessibility). Both must be captured and testable.",
    },
    {
        "question": "Design a requirements management process for a large ERP implementation project.",
        "job_role": "Business Analyst",
        "difficulty": "hard",
        "category": "system_design",
        "hint": "Cover RTM (Requirement Traceability Matrix), change control, and sign-off process.",
        "sample_answer": "Establish a Requirements Traceability Matrix (RTM) linking business needs → functional requirements → test cases → UAT sign-off. Use a formal change-control process: all requirement changes go through a CR (Change Request) with impact assessment (scope, cost, timeline) and sponsor sign-off before implementation. Baseline requirements in a version-controlled repository (Confluence/JIRA). Weekly requirements reviews with the client during development. Go-no-go criterion: UAT sign-off on all Priority 1 requirements.",
    },
]


class PracticeService:

    @staticmethod
    def list_questions(
        page: int = 1,
        per_page: int = 20,
        job_role: str | None = None,
        difficulty: str | None = None,
        category: str | None = None,
    ) -> dict:
        """List practice questions with optional filters."""

        query = PracticeQuestion.query.filter_by(is_active=True)

        if job_role:
            query = query.filter(PracticeQuestion.job_role.ilike(f"%{job_role}%"))
        if difficulty:
            query = query.filter_by(difficulty=difficulty)
        if category:
            query = query.filter_by(category=category)

        query = query.order_by(PracticeQuestion.created_at.desc())

        return paginate_query(query, page, per_page, PracticeQuestionSchema())

    @staticmethod
    def get(question_id: str) -> dict:
        """Get a single practice question."""

        question = PracticeQuestion.query.get(question_id)
        if not question:
            raise NotFoundError("Practice question not found.")

        return PracticeQuestionSchema().dump(question)

    @staticmethod
    def create(data: dict) -> dict:
        """Create a new practice question (admin only)."""

        question = PracticeQuestion(**data)
        db.session.add(question)
        db.session.commit()

        return PracticeQuestionSchema().dump(question)

    @staticmethod
    def seed() -> dict:
        """
        Seed the practice question bank.
        Safe to re-run — only inserts questions that don't already exist
        (matched by question text + job_role + difficulty + category).
        """

        created = 0
        skipped = 0

        for q_data in SEED_QUESTIONS:
            exists = PracticeQuestion.query.filter_by(
                question=q_data["question"],
                job_role=q_data["job_role"],
                difficulty=q_data["difficulty"],
                category=q_data["category"],
            ).first()

            if exists:
                skipped += 1
                continue

            question = PracticeQuestion(**q_data)
            db.session.add(question)
            created += 1

        db.session.commit()
        logger.info("Seed: %d questions created, %d skipped (already exist).", created, skipped)

        return {
            "message": f"Seeded {created} questions ({skipped} already existed).",
            "created": created,
            "skipped": skipped,
        }