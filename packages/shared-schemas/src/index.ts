import { z } from "zod";

export const severitySchema = z.enum(["critical", "high", "medium", "low", "informational"]);
export const findingKindSchema = z.enum(["verified_observation", "potential_vulnerability", "informational", "not_performed"]);
export const taskStatusSchema = z.enum(["pending", "running", "completed", "failed", "skipped", "cancelled"]);

export const findingSchema = z.object({
  id: z.string().uuid().optional(),
  title: z.string().min(1),
  description: z.string().min(1),
  severity: severitySchema,
  kind: findingKindSchema,
  confidence: z.enum(["confirmed_observation", "validated_potential", "unverified_signal", "not_applicable"]),
  agentId: z.string().min(1),
  ruleId: z.string().min(1),
  asset: z.string().optional(),
  filePath: z.string().optional(),
  lineNumber: z.number().int().positive().optional(),
  evidence: z.record(z.unknown()),
  remediation: z.string().min(1),
});

export type Finding = z.infer<typeof findingSchema>;
