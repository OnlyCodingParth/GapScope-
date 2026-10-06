import { Button } from './Button'
export function ErrorState({ message, retry }: { message: string; retry?: () => void }) { return <div className="error-state"><p>{message}</p>{retry && <Button variant="secondary" onClick={retry}>Try again</Button>}</div> }
