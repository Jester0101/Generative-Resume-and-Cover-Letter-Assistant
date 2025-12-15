"use client";

import { useCallback, useState } from "react";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { EvidencePanel } from "@/components/evidence-panel";
import { GenerationResults } from "@/components/generation-results";
import { MatchSummary } from "@/components/match-summary";
import { RequestForm } from "@/components/request-form";
import { runPipeline } from "@/lib/api";
import { PipelineResponse, RunRequest } from "@/types/pipeline";

const sampleJob = `Company: ExampleCorp
Role: Backend Engineer

We are seeking an engineer who can design, build, and maintain RESTful APIs. Responsibilities include collaborating with product managers, reviewing code, and improving system reliability. Must-have skills: Python, FastAPI, SQL, cloud deployment. Nice-to-have: Docker, Kubernetes, observability (Prometheus/Grafana).`;

const sampleProfile = `I am a software engineer with 4 years of experience building backend services.
- Built and maintained FastAPI services used by 30k monthly users.
- Led migration from monolith to microservices, improving reliability.
- Designed SQL schemas and optimized queries for analytics workloads.
- Deployed services to AWS using Docker and GitHub Actions.
- Added observability with Prometheus metrics and Grafana dashboards.`;

const defaultForm: RunRequest = {
  job_description: "",
  profile_text: "",
  company_name: "",
  role_title: "",
  use_tfidf: true,
  use_bm25: true,
  use_embeddings: false,
  use_llm_jd_classifier: false,
  use_llm_editor: true,
};

export default function Home() {
  const [form, setForm] = useState<RunRequest>(defaultForm);
  const [result, setResult] = useState<PipelineResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = useCallback(async () => {
    if (!form.job_description.trim() || !form.profile_text.trim()) {
      setError("Please provide both a job description and your profile text.");
      return;
    }
    setIsLoading(true);
    setError(null);
    setResult(null);
    try {
      const payload: RunRequest = {
        ...form,
        use_tfidf: Boolean(form.use_tfidf),
        use_bm25: Boolean(form.use_bm25),
        use_embeddings: Boolean(form.use_embeddings),
        use_llm_jd_classifier: Boolean(form.use_llm_jd_classifier),
        use_llm_editor: Boolean(form.use_llm_editor),
      };
      const data = await runPipeline(payload);
      setResult(data);
    } catch (err) {
      const message =
        err instanceof Error ? err.message : "Failed to reach the backend.";
      setError(message);
    } finally {
      setIsLoading(false);
    }
  }, [form]);

  const handleLoadSample = useCallback(() => {
    setForm((prev) => ({
      ...prev,
      job_description: sampleJob,
      profile_text: sampleProfile,
      company_name: "ExampleCorp",
      role_title: "Backend Engineer",
    }));
  }, []);

  return (
    <div className="min-h-screen bg-gradient-to-b from-background to-muted/60">
      <div className="mx-auto max-w-6xl space-y-6 px-4 py-10 lg:py-12">
        <header className="space-y-3">
          <div className="flex items-center gap-2">
            <Badge variant="secondary">Frontend</Badge>
            <Badge variant="outline">Next.js + shadcn</Badge>
            <Badge variant="outline">FastAPI backend</Badge>
          </div>
          <div className="space-y-2">
            <h1 className="text-3xl font-semibold tracking-tight md:text-4xl">
              Resume & Cover Letter Assistant
            </h1>
            <p className="max-w-3xl text-muted-foreground">
              Generate grounded resume bullets and a tailored cover letter. Paste
              the JD and your profile, configure retrieval/generation options,
              and let the backend do the heavy lifting.
            </p>
          </div>
        </header>

        {error ? (
          <Alert variant="destructive">
            <AlertTitle>Request failed</AlertTitle>
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        ) : null}

        <div className="grid gap-6 lg:grid-cols-[1.15fr_0.85fr]">
          <RequestForm
            value={form}
            onChange={setForm}
            onSubmit={handleSubmit}
            onLoadSample={handleLoadSample}
            isLoading={isLoading}
          />
          <MatchSummary
            report={result?.match_report}
            company={result?.jd.company_name || form.company_name}
            role={result?.jd.role_title || form.role_title}
            mustHaveSkills={result?.jd.must_have_skills}
            niceToHaveSkills={result?.jd.nice_to_have_skills}
            responsibilities={result?.jd.responsibilities}
            keywords={result?.jd.keywords}
            isLoading={isLoading}
          />
        </div>

        <Separator />

        <div className="grid gap-6 lg:grid-cols-2">
          <GenerationResults
            generation={result?.generation || null}
            validationWarnings={result?.validation.warnings}
            validationOk={result?.validation.ok}
            isLoading={isLoading}
          />
          <EvidencePanel
            evidenceMap={result?.evidence_map || null}
            isLoading={isLoading}
          />
        </div>
      </div>
    </div>
  );
}
