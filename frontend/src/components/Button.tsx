import type { AnchorHTMLAttributes, ButtonHTMLAttributes, ReactNode } from 'react'
import { Link } from 'react-router-dom'

type Common = { children: ReactNode; variant?: 'primary' | 'secondary' | 'ghost'; className?: string }
export function Button({ children, variant = 'primary', className = '', ...props }: Common & ButtonHTMLAttributes<HTMLButtonElement>) { return <button className={`button ${variant} ${className}`} {...props}>{children}</button> }
export function ButtonLink({ children, variant = 'primary', className = '', to, ...props }: Common & AnchorHTMLAttributes<HTMLAnchorElement> & { to: string }) { return <Link className={`button ${variant} ${className}`} to={to} {...props}>{children}</Link> }
