# config: Deployment Architecture Analysis (Netlify vs Alternatives)

## Summary
Analyze deployment options for the FastAPI backend, explaining why Netlify is suboptimal for async Python workloads and proposing better low-cost PaaS alternatives (Render, Fly.io, Railway) that natively support containerized or long-running applications.

## Scope
- **In scope**: Analysis of Netlify limitations (serverless timeouts, async/WebSockets support, Python ecosystem).
- **In scope**: Comparison of Render, Fly.io, and Railway for low-cost deployment.
- **In scope**: Environment configuration, Supabase integration, and startup commands.
- **Out of scope**: Actual deployment execution or writing IaC code in this step.

## Files to Create / Modify
| File | Action | Description |
|------|--------|-------------|
| `implementation_plan.md` | Update | Document the deployment analysis and final selection of Render. |
| `Dockerfile` | Create | Multi-stage Dockerfile using `uv` to build and run the FastAPI app. |
| `render.yaml` | Create | Infrastructure as Code configuration for Render pointing to the Docker environment. |

## Business Logic / Change Description

### 1. Why Netlify is Suboptimal for FastAPI
While Netlify is excellent for frontend applications (Jamstack), it is fundamentally a serverless platform. Deploying FastAPI on Netlify implies running it within AWS Lambda (via Netlify Functions):
- **Stateless & Timeouts**: Netlify Functions have strict execution time limits (typically 10 seconds on the free tier). Long-running tasks, like Whisper audio processing or LLM calls, will likely timeout.
- **No WebSockets / SSE**: Serverless functions cannot maintain long-lived connections. If the app needs WebSockets for real-time updates or Server-Sent Events (SSE) for streaming AI responses, Netlify will block this.
- **Cold Starts**: When a function isn't called for a while, it spins down. The next request suffers a "cold start" delay, which can be several seconds for Python applications — providing a poor UX for mobile users.
- **Adapter Overhead**: Running FastAPI on Lambda requires an ASGI adapter like `Mangum`, which adds complexity to the configuration and routing.

### 2. Proposed Alternatives (PaaS / Container-based)
For a FastAPI application, a traditional long-running container or VM is required. Here are the best low/zero-cost alternatives:

#### A. Render (Recommended for ease of use)
- **Cost**: Free tier available (spins down after 15 minutes of inactivity). Paid tier starts at $7/mo (Always On).
- **Setup**: Can automatically build Python apps from a repo or use a `Dockerfile`.
- **Start Command**: `uv run uvicorn main:app --host 0.0.0.0 --port $PORT`
- **Pros**: Extremely simple setup, automatic deployments from GitHub.
- **Cons**: Free tier sleep/wake cycle causes a 30-60 second delay on the first request.

#### B. Fly.io (Recommended for low latency & global reach)
- **Cost**: Generous free tier (up to 3 small 256MB VMs, though 256MB might be tight for heavy Python apps).
- **Setup**: Requires a `Dockerfile` and a `fly.toml` config file. Deploys via Fly CLI.
- **Start Command**: `CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]` (inside Dockerfile)
- **Pros**: Can deploy the backend in the same region as the Supabase database for ultra-low latency. True VM instances (supports WebSockets).
- **Cons**: Docker knowledge required. Strict memory limits on the free tier.

#### C. Railway (Recommended for Developer Experience)
- **Cost**: $5/mo minimum (Trial available, pay-as-you-go). No permanent free tier.
- **Setup**: Uses Nixpacks. Just connect the repo and it automatically detects Python, installs dependencies, and deploys without a Dockerfile.
- **Start Command**: Auto-detected, but can be overridden in the dashboard.
- **Pros**: Best developer experience, no cold starts, easy environment variable management.
- **Cons**: Not completely free long-term.

### 3. Environment Configuration & Integration
Regardless of the platform chosen, the environment will be configured as follows:

1. **Supabase Integration**:
   - `SUPABASE_URL`: The URL of the Supabase project.
   - `SUPABASE_SERVICE_ROLE_KEY`: Required for backend operations (bypassing RLS for admin tasks).
   - These variables will be injected via the platform's secret manager (Render Dashboard, Fly Secrets, or Railway Variables).
2. **Server Configuration**:
   - The application must bind to `0.0.0.0` and listen to the port provided by the platform (usually via the `$PORT` environment variable).

## Acceptance Criteria
- [x] Analyze Netlify limitations.
- [x] Propose container-based alternatives.
- [x] Define environment requirements for Supabase.

## Open Questions / Risk Alerts
- **Clarification on "tf"**: In your request, you mentioned "conectarlo con tf". Did you mean:
  - Connecting it with the **Front-end** (React Native mobile app)?
  - Deploying it using **Terraform** (Infrastructure as Code)?
  - Integrating it with **TensorFlow** (for ML)?
- **Cold Starts**: Are we okay with the 30-60 second cold start on Render's free tier, or would we prefer to spend ~$5-7/month for an "Always On" instance (Render/Railway)?
- **Memory Requirements**: If we process audio or run heavy ML libraries directly in the API, we might exceed the 256MB/512MB RAM limits of the free tiers. Should we plan for a paid tier from the start?
