import * as React from 'react'
import clsx from 'clsx'

export type BadgeProps = React.HTMLAttributes<HTMLSpanElement> & {
	variant?: 'default' | 'secondary'
}

const variantClasses: Record<NonNullable<BadgeProps['variant']>, string> = {
	default: 'bg-blue-100 text-blue-800',
	secondary: 'bg-gray-100 text-gray-800'
}

export function Badge({ className, children, variant = 'default', ...props }: BadgeProps) {
	return (
		<span
			className={clsx('inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium', variantClasses[variant], className)}
			{...props}
		>
			{children}
		</span>
	)
}