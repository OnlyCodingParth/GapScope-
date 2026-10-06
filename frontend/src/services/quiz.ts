import { requestJson } from './apiClient'
import type { AiAnalysis, AttemptResult, LearningGapReport, PracticeSession, QuizQuestion } from '../types/api'

export async function getQuizQuestions(): Promise<QuizQuestion[]> {
  const body = await requestJson('/quiz/questions')
  if (!Array.isArray(body) || body.some(question => !question || typeof question !== 'object' || !Array.isArray((question as QuizQuestion).options))) throw new Error('Unexpected quiz response.')
  return body as QuizQuestion[]
}

export async function submitQuiz(responses: { question_id: string; selected_answer: string }[]): Promise<AttemptResult> {
  return await requestJson('/attempts', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ responses }) }) as AttemptResult
}

export async function getLearningGapReport(attemptId: string): Promise<LearningGapReport> {
  return await requestJson(`/attempts/${attemptId}/report`) as LearningGapReport
}

export async function startTargetedPractice(sourceAttemptId: string): Promise<PracticeSession> {
  return await requestJson('/practice', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ source_attempt_id: sourceAttemptId }) }) as PracticeSession
}

export async function submitTargetedPractice(practiceId: string, stage: 'practice' | 'retest', responses: { question_id: string; selected_answer: string }[]): Promise<PracticeSession> {
  return await requestJson(`/practice/${practiceId}/submit`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ stage, responses }) }) as PracticeSession
}

export async function getAiAnalysis(attemptId: string): Promise<AiAnalysis> {
  return await requestJson('/ai/analyze', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ attempt_id: attemptId }) }) as AiAnalysis
}
