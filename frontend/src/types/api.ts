export type HealthResponse = { status: 'ok'; service: 'gapscope-backend' }
export type QuizQuestion = { id: string; question_text: string; concept: string; difficulty: string; question_type: string; options: string[] }
export type QuestionResult = { question_id: string; selected_answer: string; is_correct: number; misconception_id: string | null; misconception_name: string | null }
export type AttemptResult = { id: string; total_questions: number; correct_answers: number; incorrect_answers: number; score: number; percentage: number; results: QuestionResult[]; detected_misconceptions: { id: string; name: string }[] }
export type LearningGap = { misconception_id: string; misconception_name: string; description: string; evidence_count: number; confidence: 'low' | 'medium' | 'high'; evidence: { question_id: string; question_text: string; concept: string; selected_answer: string }[]; recommendation: string }
export type LearningGapReport = { attempt_id: string; total_questions: number; correct_answers: number; gaps: LearningGap[]; chart: { misconception_id: string; label: string; evidence_count: number }[] }
export type PracticeStage = { total_questions: number; complete: boolean; correct_answers?: number; questions?: QuizQuestion[] }
export type PracticeSession = { id: string; source_attempt_id: string; focus: { misconception_id: string; name: string; description: string }; before: { evidence_count: number; confidence: string }; practice: PracticeStage; retest: PracticeStage; comparison: null | { before_evidence_count: number; before_confidence: string; retest_correct_answers: number; retest_total_questions: number; status: 'improvement_detected' | 'insufficient_evidence'; message: string } }
export type AiInsight = { misconception_id: string; explanation: string; recommendation: string }
export type AiAnalysis = { source: 'llm' | 'fallback'; available: boolean; message: string; insights: AiInsight[]; practice_questions: unknown[] }
export type ApiErrorKind = 'network' | 'timeout' | 'http' | 'invalid-response'
export class ApiError extends Error {
  readonly kind: ApiErrorKind
  readonly status?: number
  constructor(kind: ApiErrorKind, message: string, status?: number) { super(message); this.name = 'ApiError'; this.kind = kind; this.status = status }
}
