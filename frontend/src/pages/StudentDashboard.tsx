import { useState } from 'react'
import { Badge } from '../components/Badge'
import { Button } from '../components/Button'
import { Card } from '../components/Card'
import { EmptyState } from '../components/EmptyState'
import { ErrorState } from '../components/ErrorState'
import { LoadingState } from '../components/LoadingState'
import { PageContainer } from '../components/PageContainer'
import { getAiAnalysis, getLearningGapReport, getQuizQuestions, startTargetedPractice, submitQuiz, submitTargetedPractice } from '../services/quiz'
import type { AiAnalysis, AttemptResult, LearningGapReport, PracticeSession, QuizQuestion } from '../types/api'
import { useDocumentTitle } from './useDocumentTitle'

export function StudentDashboard() {
  useDocumentTitle('Student quiz | GapScope')
  const [questions, setQuestions] = useState<QuizQuestion[] | null>(null)
  const [answers, setAnswers] = useState<Record<string, string>>({})
  const [result, setResult] = useState<AttemptResult | null>(null)
  const [report, setReport] = useState<LearningGapReport | null>(null)
  const [practice, setPractice] = useState<PracticeSession | null>(null)
  const [practiceStage, setPracticeStage] = useState<'practice' | 'retest'>('practice')
  const [practiceAnswers, setPracticeAnswers] = useState<Record<string, string>>({})
  const [practiceMessage, setPracticeMessage] = useState('')
  const [practiceSubmitting, setPracticeSubmitting] = useState(false)
  const [aiAnalysis, setAiAnalysis] = useState<AiAnalysis | null>(null)
  const [aiLoading, setAiLoading] = useState(false)
  const [state, setState] = useState<'ready' | 'loading' | 'submitting' | 'failed'>('ready')
  const [message, setMessage] = useState('')

  async function startQuiz() {
    setState('loading')
    setMessage('')
    try {
      setQuestions(await getQuizQuestions())
      setAnswers({})
      setResult(null)
      setReport(null)
      setPractice(null)
      setAiAnalysis(null)
      setState('ready')
    } catch {
      setMessage('The quiz could not be loaded. Confirm the backend is running and try again.')
      setState('failed')
    }
  }

  async function generateAiInsight() {
    if (!report) return
    setAiLoading(true)
    try {
      setAiAnalysis(await getAiAnalysis(report.attempt_id))
    } catch {
      setAiAnalysis({ source: 'fallback', available: false, message: 'AI insight is unavailable. Your verified report and practice flow still work.', insights: [], practice_questions: [] })
    } finally {
      setAiLoading(false)
    }
  }

  async function beginPractice() {
    if (!report) return
    setPracticeMessage('')
    try {
      setPractice(await startTargetedPractice(report.attempt_id))
      setPracticeStage('practice')
      setPracticeAnswers({})
    } catch {
      setPracticeMessage('Targeted practice could not be started. Please try again.')
    }
  }

  async function submitPractice() {
    if (!practice) return
    const questions = practice[practiceStage].questions ?? []
    if (questions.some(question => !practiceAnswers[question.id])) {
      setPracticeMessage('Choose an answer for every assigned question before submitting.')
      return
    }
    setPracticeSubmitting(true)
    setPracticeMessage('')
    try {
      setPractice(await submitTargetedPractice(practice.id, practiceStage, questions.map(question => ({ question_id: question.id, selected_answer: practiceAnswers[question.id] }))))
      setPracticeAnswers({})
    } catch {
      setPracticeMessage('This practice submission could not be saved. Please try again.')
    } finally {
      setPracticeSubmitting(false)
    }
  }

  async function submit() {
    if (!questions || questions.some(question => !answers[question.id])) {
      setMessage('Choose an answer for every question before submitting.')
      setState('failed')
      return
    }
    setState('submitting')
    setMessage('')
    try {
      const submitted = await submitQuiz(questions.map(question => ({ question_id: question.id, selected_answer: answers[question.id] })))
      setResult(submitted)
      setReport(await getLearningGapReport(submitted.id))
      setState('ready')
    } catch {
      setMessage('Your quiz was submitted, but the learning-gap report could not be loaded. Please try again.')
      setState('failed')
    }
  }

  if (result) return <PageContainer><section className="dashboard"><Badge>Learning Gap Report</Badge><h1>Quadratic Equations result</h1><Card><p className="result-score">{result.score} / {result.total_questions}</p><p>{result.percentage}% correct · {result.incorrect_answers} incorrect</p>{result.detected_misconceptions.length > 0 ? <><h2>Mapped misconceptions</h2><ul>{result.detected_misconceptions.map(item => <li key={item.id}>{item.name}</li>)}</ul></> : <p>All answers were correct. No misconceptions were mapped.</p>}</Card>{report ? <LearningGapReportView report={report} onStartPractice={beginPractice} onGenerateAi={generateAiInsight} aiLoading={aiLoading} aiAnalysis={aiAnalysis} /> : <Card><p>{state === 'failed' ? message : 'Preparing your learning-gap report…'}</p></Card>}{practiceMessage && <ErrorState message={practiceMessage} />}{practice && <TargetedPractice practice={practice} stage={practiceStage} answers={practiceAnswers} submitting={practiceSubmitting} onChoose={(questionId, answer) => setPracticeAnswers(current => ({ ...current, [questionId]: answer }))} onSubmit={submitPractice} onStartRetest={() => { setPracticeStage('retest'); setPracticeAnswers({}); setPracticeMessage('') }} />}<Button onClick={startQuiz}>Start another quiz</Button></section></PageContainer>

  return <PageContainer><section className="dashboard"><Badge>Student preview</Badge><h1>Quadratic Equations quiz</h1>{questions === null ? <EmptyState title="Ready to check your understanding"><p>This demo quiz grades your answers and maps only selected wrong options to the existing taxonomy.</p><Button onClick={startQuiz}>Start Quadratic Equations Quiz</Button></EmptyState> : <form className="quiz-form" onSubmit={event => { event.preventDefault(); void submit() }}>{questions.map((question, index) => <Card key={question.id}><p className="question-meta">Question {index + 1} · {question.difficulty}</p><fieldset><legend>{question.question_text}</legend>{question.options.map(option => <label className="answer-option" key={option}><input type="radio" name={question.id} value={option} checked={answers[question.id] === option} onChange={() => setAnswers(current => ({ ...current, [question.id]: option }))} />{option}</label>)}</fieldset></Card>)}<Button type="submit" disabled={state === 'submitting'}>{state === 'submitting' ? 'Submitting quiz…' : 'Submit quiz'}</Button></form>}{state === 'loading' && <LoadingState />}{state === 'failed' && <ErrorState message={message} retry={questions === null ? startQuiz : undefined} />}</section></PageContainer>
}

function LearningGapReportView({ report, onStartPractice, onGenerateAi, aiLoading, aiAnalysis }: { report: LearningGapReport; onStartPractice: () => void; onGenerateAi: () => void; aiLoading: boolean; aiAnalysis: AiAnalysis | null }) {
  if (report.gaps.length === 0) return <Card><h2>Learning Gap Report</h2><p>No learning gaps were detected from this attempt. Every submitted response was correct or had no mapped misconception.</p></Card>
  const highestCount = Math.max(...report.chart.map(item => item.evidence_count))
  return <section className="gap-report" aria-labelledby="gap-report-heading"><h2 id="gap-report-heading">Learning Gap Report</h2><Card><h3>Evidence chart</h3><p className="report-intro">Each bar counts this attempt’s incorrect responses mapped to that misconception.</p><div className="gap-chart" role="img" aria-label="Detected misconceptions by evidence count">{report.chart.map(item => <div className="chart-row" key={item.misconception_id}><span>{item.label}</span><div className="chart-track"><div className="chart-bar" style={{ width: `${Math.max(12, item.evidence_count / highestCount * 100)}%` }} /></div><strong>{item.evidence_count}</strong></div>)}</div></Card>{report.gaps.map(gap => <Card key={gap.misconception_id}><h3>{gap.misconception_name}</h3><p><strong>Confidence:</strong> {gap.confidence} ({gap.evidence_count} supporting {gap.evidence_count === 1 ? 'response' : 'responses'})</p><p>{gap.description}</p><h4>Evidence</h4><ul>{gap.evidence.map(item => <li key={item.question_id}><strong>{item.question_id}:</strong> {item.question_text} <span className="evidence-answer">Selected: {item.selected_answer}</span></li>)}</ul><h4>Recommendation</h4><p>{gap.recommendation}</p></Card>)}<Card><h3>AI Learning Insight</h3>{aiAnalysis ? <><p>{aiAnalysis.message}</p>{aiAnalysis.insights.map(insight => <div key={insight.misconception_id}><h4>AI explanation</h4><p>{insight.explanation}</p><h4>Personalized recommendation</h4><p>{insight.recommendation}</p></div>)}</> : <p>Generate a concise explanation and personalized recommendation from the verified evidence.</p>}<Button variant="secondary" onClick={onGenerateAi} disabled={aiLoading}>{aiLoading ? 'Generating AI insight…' : 'Generate AI Insight'}</Button></Card><Button onClick={onStartPractice}>Practice These Weaknesses</Button></section>
}

function TargetedPractice({ practice, stage, answers, submitting, onChoose, onSubmit, onStartRetest }: { practice: PracticeSession; stage: 'practice' | 'retest'; answers: Record<string, string>; submitting: boolean; onChoose: (questionId: string, answer: string) => void; onSubmit: () => void; onStartRetest: () => void }) {
  if (practice.comparison) return <section className="targeted-practice"><Card><Badge>Before / After</Badge><h2>Improvement result</h2><p><strong>Before practice:</strong> {practice.focus.name} — {practice.before.evidence_count} supporting errors ({practice.before.confidence} confidence)</p><p><strong>Practice:</strong> {practice.practice.correct_answers} / {practice.practice.total_questions} correct</p><p><strong>Retest:</strong> {practice.comparison.retest_correct_answers} / {practice.comparison.retest_total_questions} correct</p><p className="comparison-result">{practice.comparison.message}</p></Card></section>
  const current = practice[stage]
  if (stage === 'practice' && current.complete) return <section className="targeted-practice"><Card><Badge>Practice complete</Badge><h2>Targeted Practice result</h2><p>{practice.focus.name}: {current.correct_answers} / {current.total_questions} correct.</p><Button onClick={onStartRetest}>Start retest</Button></Card></section>
  const questions = current.questions ?? []
  return <section className="targeted-practice"><Badge>{stage === 'practice' ? 'Targeted Practice' : 'Retest'}</Badge><h2>Focus: {practice.focus.name}</h2><p>{practice.focus.description}</p><form className="quiz-form" onSubmit={event => { event.preventDefault(); void onSubmit() }}>{questions.map((question, index) => <Card key={question.id}><p className="question-meta">{stage === 'practice' ? 'Practice' : 'Retest'} question {index + 1} · {question.difficulty}</p><fieldset><legend>{question.question_text}</legend>{question.options.map(option => <label className="answer-option" key={option}><input type="radio" name={`${stage}-${question.id}`} value={option} checked={answers[question.id] === option} onChange={() => onChoose(question.id, option)} />{option}</label>)}</fieldset></Card>)}<Button type="submit" disabled={submitting}>{submitting ? 'Submitting…' : `Submit ${stage === 'practice' ? 'practice' : 'retest'}`}</Button></form></section>
}
