"use client";

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
import { EvidenceItem } from "@/types/pipeline";

type EvidencePanelProps = {
  evidenceMap?: Record<string, EvidenceItem> | null;
  isLoading?: boolean;
};

export function EvidencePanel({ evidenceMap, isLoading }: EvidencePanelProps) {
  if (isLoading) {
    return (
      <Card className="h-full border-border/60 shadow-sm">
        <CardHeader>
          <CardTitle>Evidence map</CardTitle>
          <CardDescription>Chunks supporting each requirement</CardDescription>
        </CardHeader>
        <CardContent className="space-y-2">
          <Skeleton className="h-4 w-full" />
          <Skeleton className="h-4 w-4/5" />
          <Skeleton className="h-4 w-3/5" />
        </CardContent>
      </Card>
    );
  }

  if (!evidenceMap || !Object.keys(evidenceMap).length) {
    return (
      <Card className="h-full border-dashed border-border/70 shadow-none">
        <CardHeader>
          <CardTitle>Evidence map</CardTitle>
          <CardDescription>
            Inspect which profile chunks support each requirement.
          </CardDescription>
        </CardHeader>
        <CardContent className="text-sm text-muted-foreground">
          Results will appear once a request is completed.
        </CardContent>
      </Card>
    );
  }

  const entries = Object.values(evidenceMap).sort(
    (a, b) => Number(b.score) - Number(a.score)
  );

  return (
    <Card className="flex h-full flex-col border-border/60 shadow-sm overflow-hidden">
      <CardHeader className="space-y-2 flex-shrink-0">
        <CardTitle>Evidence map</CardTitle>
        <CardDescription>
          How the backend grounded each requirement in your profile chunks.
        </CardDescription>
      </CardHeader>
      <CardContent className="flex flex-1 flex-col overflow-hidden p-0 min-h-0">
        <ScrollArea className="flex-1 min-h-0">
          <div className="space-y-3 px-6 pb-6">
            {entries.map((item, idx) => (
              <div
                key={`${item.requirement}-${idx}`}
                className="space-y-2 rounded-lg border border-border/70 bg-card px-3 py-2"
              >
                <div className="flex flex-wrap items-center gap-2">
                  <Badge variant={item.matched ? "secondary" : "outline"}>
                    {item.matched ? "Matched" : "Missing"}
                  </Badge>
                  <Badge variant="outline">
                    Score: {Number(item.score).toFixed(2)}
                  </Badge>
                </div>
                <div className="text-sm font-medium leading-snug break-words">
                  {item.requirement}
                </div>
                <div className="space-y-2 pt-1">
                  {item.chunks.map((chunk) => (
                    <div
                      key={chunk.chunk_id}
                      className="rounded-md border border-border/60 bg-background/60 px-2 py-1"
                    >
                      <div className="flex flex-wrap items-center justify-between gap-1 text-[11px] text-muted-foreground">
                        <span className="font-medium">
                          {chunk.section || "Profile"}
                        </span>
                        <span className="tabular-nums">
                          final {chunk.scores.final.toFixed(2)} · tfidf{" "}
                          {chunk.scores.tfidf.toFixed(2)} · bm25{" "}
                          {chunk.scores.bm25.toFixed(2)}
                        </span>
                      </div>
                      <p className="mt-1 line-clamp-3 break-words text-xs leading-snug">
                        {chunk.text}
                      </p>
                      {chunk.skills_found.length ? (
                        <div className="mt-1 flex flex-wrap gap-1">
                          {chunk.skills_found.map((skill) => (
                            <Badge
                              key={skill}
                              variant="outline"
                              className="text-[10px]"
                            >
                              {skill}
                            </Badge>
                          ))}
                        </div>
                      ) : null}
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </ScrollArea>
       
      </CardContent>
    </Card>
  );
}

