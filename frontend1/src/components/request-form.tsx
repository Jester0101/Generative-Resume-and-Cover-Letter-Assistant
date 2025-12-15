"use client";

import { useMemo } from "react";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Separator } from "@/components/ui/separator";
import { Switch } from "@/components/ui/switch";
import { Textarea } from "@/components/ui/textarea";
import { RunRequest } from "@/types/pipeline";

type RequestFormProps = {
  value: RunRequest;
  isLoading: boolean;
  onChange: (value: RunRequest) => void;
  onSubmit: () => void;
  onLoadSample: () => void;
};

type ToggleKey =
  | "use_tfidf"
  | "use_bm25"
  | "use_embeddings"
  | "use_llm_jd_classifier"
  | "use_llm_editor";

export function RequestForm({
  value,
  isLoading,
  onChange,
  onSubmit,
  onLoadSample,
}: RequestFormProps) {
  const toggles = useMemo(
    () =>
      [
        {
          key: "use_tfidf" as ToggleKey,
          label: "TF-IDF",
          description: "Classic keyword retrieval.",
        },
        {
          key: "use_bm25" as ToggleKey,
          label: "BM25",
          description: "Strong baseline for textual relevance.",
        },
        {
          key: "use_embeddings" as ToggleKey,
          label: "Embeddings",
          description: "Semantic matching (requires embeddings model).",
        },
        {
          key: "use_llm_jd_classifier" as ToggleKey,
          label: "LLM JD Classifier",
          description: "Let the LLM refine parsed JD skills.",
        },
        {
          key: "use_llm_editor" as ToggleKey,
          label: "LLM Editor",
          description: "Polish generation while keeping grounding.",
        },
      ] satisfies {
        key: ToggleKey;
        label: string;
        description: string;
      }[],
    [],
  );

  return (
    <Card className="h-fit border-border/60 shadow-sm">
      <CardHeader className="space-y-1">
        <CardTitle>Provide job and profile details</CardTitle>
        <CardDescription>
          Paste the raw job description and your resume/profile. You can also
          toggle retrieval/generation options to match the backend switches.
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="space-y-2">
          <Label htmlFor="job_description">Job description</Label>
          <Textarea
            id="job_description"
            placeholder="Paste the full job description..."
            minLength={40}
            rows={8}
            value={value.job_description}
            onChange={(e) =>
              onChange({ ...value, job_description: e.target.value })
            }
            disabled={isLoading}
          />
        </div>
        <div className="space-y-2">
          <Label htmlFor="profile_text">Your profile / resume</Label>
          <Textarea
            id="profile_text"
            placeholder="Paste your resume or profile text..."
            minLength={40}
            rows={8}
            value={value.profile_text}
            onChange={(e) =>
              onChange({ ...value, profile_text: e.target.value })
            }
            disabled={isLoading}
          />
        </div>
        <div className="grid gap-3 sm:grid-cols-2">
          <div className="space-y-2">
            <Label htmlFor="company_name">Company (optional)</Label>
            <Input
              id="company_name"
              placeholder="e.g., ExampleCorp"
              value={value.company_name || ""}
              onChange={(e) =>
                onChange({ ...value, company_name: e.target.value })
              }
              disabled={isLoading}
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="role_title">Role (optional)</Label>
            <Input
              id="role_title"
              placeholder="e.g., Backend Engineer"
              value={value.role_title || ""}
              onChange={(e) =>
                onChange({ ...value, role_title: e.target.value })
              }
              disabled={isLoading}
            />
          </div>
        </div>
        <Separator />
        <div className="grid gap-3 md:grid-cols-2 lg:grid-cols-3">
          {toggles.map((item) => (
            <div
              key={item.key}
              className="flex items-start justify-between rounded-lg border border-border/70 px-3 py-2"
            >
              <div className="space-y-1 pr-3">
                <p className="text-sm font-medium leading-none">{item.label}</p>
                <p className="text-sm text-muted-foreground">
                  {item.description}
                </p>
              </div>
              <Switch
                checked={Boolean(value[item.key])}
                onCheckedChange={(checked) => onChange({ ...value, [item.key]: checked })}
                disabled={isLoading}
              />
            </div>
          ))}
        </div>
      </CardContent>
      <CardFooter className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div className="flex items-center gap-2 text-sm text-muted-foreground">
          <span>Need a quick trial?</span>
          <Button
            type="button"
            variant="secondary"
            size="sm"
            onClick={onLoadSample}
            disabled={isLoading}
          >
            Fill sample data
          </Button>
        </div>
        <div className="flex w-full gap-2 sm:w-auto">
          <Button
            type="button"
            variant="outline"
            className="w-full sm:w-auto"
            onClick={() =>
              onChange({
                job_description: "",
                profile_text: "",
                company_name: "",
                role_title: "",
                use_tfidf: true,
                use_bm25: true,
                use_embeddings: false,
                use_llm_jd_classifier: false,
                use_llm_editor: true,
              })
            }
            disabled={isLoading}
          >
            Clear
          </Button>
          <Button
            type="button"
            className="w-full sm:w-auto"
            onClick={onSubmit}
            disabled={isLoading}
          >
            {isLoading ? "Generating..." : "Generate outputs"}
          </Button>
        </div>
      </CardFooter>
    </Card>
  );
}

