"use client";

import { Badge } from "@/components/ui/badge";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Separator } from "@/components/ui/separator";
import { Skeleton } from "@/components/ui/skeleton";
import { MatchReport } from "@/types/pipeline";

type MatchSummaryProps = {
  report?: MatchReport | null;
  company?: string;
  role?: string;
  mustHaveSkills?: string[];
  niceToHaveSkills?: string[];
  responsibilities?: string[];
  keywords?: string[];
  isLoading?: boolean;
};

export function MatchSummary({
  report,
  company,
  role,
  mustHaveSkills,
  niceToHaveSkills,
  responsibilities,
  keywords,
  isLoading,
}: MatchSummaryProps) {
  if (isLoading) {
    return (
      <Card className="h-full border-border/60 shadow-sm">
        <CardHeader className="space-y-2">
          <CardTitle>Match overview</CardTitle>
          <CardDescription>Scoring your fit to the JD</CardDescription>
        </CardHeader>
        <CardContent className="space-y-3">
          <Skeleton className="h-6 w-32" />
          <Skeleton className="h-4 w-full" />
          <Skeleton className="h-4 w-4/5" />
          <Skeleton className="h-4 w-3/5" />
        </CardContent>
      </Card>
    );
  }

  if (!report) {
    return (
      <Card className="h-full border-dashed border-border/70 shadow-none">
        <CardHeader>
          <CardTitle>Match overview</CardTitle>
          <CardDescription>
            Submit a request to see how your profile aligns.
          </CardDescription>
        </CardHeader>
        <CardContent className="flex flex-wrap gap-2 text-sm text-muted-foreground">
          <Badge variant="outline">Scores</Badge>
          <Badge variant="outline">Matched skills</Badge>
          <Badge variant="outline">Missing skills</Badge>
        </CardContent>
      </Card>
    );
  }

  const ScoreRow = ({
    label,
    value,
  }: {
    label: string;
    value: number;
  }) => (
    <div className="space-y-2">
      <div className="flex items-center justify-between text-sm font-medium">
        <span>{label}</span>
        <span className="text-muted-foreground">{value}%</span>
      </div>
      <div className="h-2 rounded-full bg-muted">
        <div
          className="h-full rounded-full bg-primary"
          style={{ width: `${Math.min(Math.max(value, 0), 100)}%` }}
        />
      </div>
    </div>
  );

  return (
    <Card className="h-full border-border/60 shadow-sm">
      <CardHeader className="space-y-2">
        <div className="flex items-center gap-2">
          <CardTitle>Match overview</CardTitle>
          {company ? <Badge variant="secondary">{company}</Badge> : null}
          {role ? <Badge variant="outline">{role}</Badge> : null}
        </div>
        <CardDescription>
          Snapshot of how the backend scored this profile.
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <ScoreRow label="Overall" value={report.match_score_overall} />
        <ScoreRow label="Must have" value={report.match_score_must} />
        <ScoreRow label="Nice to have" value={report.match_score_nice} />
        <Separator />
        <div className="grid gap-3 md:grid-cols-2">
          <div className="space-y-2">
            <div className="text-sm font-semibold text-foreground/90">
              Matched requirements
            </div>
            <div className="flex flex-wrap gap-2">
              {report.matched_requirements.length ? (
                report.matched_requirements.map((item) => (
                  <Badge key={item} variant="outline">
                    {item}
                  </Badge>
                ))
              ) : (
                <p className="text-sm text-muted-foreground">None captured.</p>
              )}
            </div>
          </div>
          <div className="space-y-2">
            <div className="text-sm font-semibold text-foreground/90">
              Missing requirements
            </div>
            <div className="flex flex-wrap gap-2">
              {report.missing_requirements.length ? (
                report.missing_requirements.map((item) => (
                  <Badge key={item} variant="secondary">
                    {item}
                  </Badge>
                ))
              ) : (
                <p className="text-sm text-muted-foreground">
                  No gaps detected.
                </p>
              )}
            </div>
          </div>
        </div>
        {(mustHaveSkills && mustHaveSkills.length) ||
        (niceToHaveSkills && niceToHaveSkills.length) ||
        (responsibilities && responsibilities.length) ||
        (keywords && keywords.length) ? (
          <>
            <Separator />
            <div className="grid gap-3 md:grid-cols-2">
              {mustHaveSkills && mustHaveSkills.length ? (
                <div className="space-y-1">
                  <div className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">
                    Must-have skills
                  </div>
                  <div className="flex flex-wrap gap-1.5">
                    {mustHaveSkills.map((skill) => (
                      <Badge key={skill} variant="outline">
                        {skill}
                      </Badge>
                    ))}
                  </div>
                </div>
              ) : null}
              {niceToHaveSkills && niceToHaveSkills.length ? (
                <div className="space-y-1">
                  <div className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">
                    Nice-to-have skills
                  </div>
                  <div className="flex flex-wrap gap-1.5">
                    {niceToHaveSkills.map((skill) => (
                      <Badge key={skill} variant="outline">
                        {skill}
                      </Badge>
                    ))}
                  </div>
                </div>
              ) : null}
              {responsibilities && responsibilities.length ? (
                <div className="space-y-1 md:col-span-2">
                  <div className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">
                    Responsibilities
                  </div>
                  <ul className="list-disc space-y-0.5 pl-4 text-xs text-muted-foreground">
                    {responsibilities.map((item, idx) => (
                      <li key={idx}>{item}</li>
                    ))}
                  </ul>
                </div>
              ) : null}
              {keywords && keywords.length ? (
                <div className="space-y-1 md:col-span-2">
                  <div className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">
                    Keywords
                  </div>
                  <div className="flex flex-wrap gap-1.5">
                    {keywords.map((kw) => (
                      <Badge key={kw} variant="outline">
                        {kw}
                      </Badge>
                    ))}
                  </div>
                </div>
              ) : null}
            </div>
          </>
        ) : null}
      </CardContent>
    </Card>
  );
}

