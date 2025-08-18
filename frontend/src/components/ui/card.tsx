import * as React from 'react'
import clsx from 'clsx'

export function Card({ className, ...props }: React.HTMLAttributes<HTMLDivElement>) {
	return <div className={clsx('rounded-lg border bg-white text-gray-900 shadow-sm', className)} {...props} />
}

export function CardHeader({ className, ...props }: React.HTMLAttributes<HTMLDivElement>) {
	return <div className={clsx('p-6 border-b', className)} {...props} />
}

export function CardTitle({ className, ...props }: React.HTMLAttributes<HTMLHeadingElement>) {
	return <h3 className={clsx('text-2xl font-semibold leading-none tracking-tight', className)} {...props} />
}

export function CardDescription({ className, ...props }: React.HTMLAttributes<HTMLParagraphElement>) {
	return <p className={clsx('text-sm text-gray-500', className)} {...props} />
}

export function CardContent({ className, ...props }: React.HTMLAttributes<HTMLDivElement>) {
	return <div className={clsx('p-6', className)} {...props} />
}