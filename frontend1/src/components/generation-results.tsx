"use client";

import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Badge } from "@/components/ui/badge";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Separator } from "@/components/ui/separator";
import { Skeleton } from "@/components/ui/skeleton";
import { Generation, ValidationWarning } from "@/types/pipeline";

type GenerationResultsProps = {
  generation?: Generation | null;
  validationWarnings?: ValidationWarning[];
  validationOk?: boolean;
  isLoading?: boolean;
};

export function GenerationResults({
  generation,
  validationWarnings,
  validationOk,
  isLoading,
}: GenerationResultsProps) {
  const warnings = [
    ...(generation?.warnings || []),
    ...(validationWarnings || []),
  ];

  if (isLoading) {
    return (
      <Card className="h-full border-border/60 shadow-sm">
        <CardHeader>
          <CardTitle>Outputs</CardTitle>
          <CardDescription>Resume bullets and cover letter</CardDescription>
        </CardHeader>
        <CardContent className="space-y-3">
          <Skeleton className="h-5 w-32" />
          <Skeleton className="h-24 w-full" />
          <Skeleton className="h-5 w-28" />
          <Skeleton className="h-24 w-full" />
        </CardContent>
      </Card>
    );
  }

  if (!generation) {
    return (
      <Card className="h-full border-dashed border-border/70 shadow-none">
        <CardHeader>
          <CardTitle>Outputs</CardTitle>
          <CardDescription>
            Generated resume bullets and a grounded cover letter will appear
            here.
          </CardDescription>
        </CardHeader>
        <CardContent className="text-sm text-muted-foreground">
          Run the pipeline to inspect the structured output from the backend.
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="h-full border-border/60 shadow-sm">
      <CardHeader className="space-y-2">
        <div className="flex items-center gap-2">
          <CardTitle>Outputs</CardTitle>
          {typeof validationOk === "boolean" ? (
            <Badge variant={validationOk ? "outline" : "destructive"}>
              {validationOk ? "Validation OK" : "Validation issues"}
            </Badge>
          ) : null}
        </div>
        <CardDescription>
          Grounded resume bullets and a tailored cover letter.
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-5">
        {warnings.length ? (
          <Alert variant="default">
            <AlertTitle>Warnings</AlertTitle>
            <AlertDescription className="space-y-1">
              {warnings.map((warning, idx) => (
                <div key={idx} className="text-sm">
                  {typeof warning === "string"
                    ? warning
                    : `${warning.code}: ${warning.message}`}
                </div>
              ))}
            </AlertDescription>
          </Alert>
        ) : null}

        <section className="space-y-3">
          <div className="flex items-center gap-2">
            <h3 className="text-base font-semibold">Resume bullets</h3>
            <Badge variant="outline">
              {generation.resume_bullets.length} items
            </Badge>
          </div>
          <div className="space-y-3">
            {generation.resume_bullets.map((bullet, idx) => (
              <div
                key={idx}
                className="rounded-lg border border-border/70 bg-card px-3 py-2"
              >
                <div className="text-sm font-medium">{bullet.text}</div>
                <div className="mt-2 flex flex-wrap gap-2">
                  {bullet.skills_used?.map((skill) => (
                    <Badge key={skill} variant="secondary">
                      {skill}
                    </Badge>
                  ))}
                </div>
                <div className="mt-2 text-xs text-muted-foreground">
                  Evidence: {bullet.evidence_chunks.join(", ")}
                </div>
              </div>
            ))}
          </div>
        </section>

        <Separator />

        <section className="space-y-3">
          <div className="flex items-center gap-2">
            <h3 className="text-base font-semibold">Cover letter</h3>
            <Badge variant="secondary">Grounded</Badge>
          </div>
          <ScrollArea className="max-h-[320px] rounded-lg border border-border/70 bg-card px-3 py-2">
            <p className="whitespace-pre-wrap text-sm leading-relaxed">
              {generation.cover_letter.text}
            </p>
            <div className="mt-2 text-xs text-muted-foreground">
              Evidence: {generation.cover_letter.evidence_chunks.join(", ")}
            </div>
          </ScrollArea>
        </section>
      </CardContent>
    </Card>
  );
}

