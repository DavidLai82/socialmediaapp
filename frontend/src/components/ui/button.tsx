import * as React from 'react'
import clsx from 'clsx'

export type ButtonProps = React.ButtonHTMLAttributes<HTMLButtonElement> & {
	variant?: 'default' | 'outline' | 'secondary'
	size?: 'sm' | 'md' | 'lg'
}

const variantClasses: Record<NonNullable<ButtonProps['variant']>, string> = {
	default: 'bg-blue-600 text-white hover:bg-blue-700',
	outline: 'border border-gray-300 text-gray-900 hover:bg-gray-50',
	secondary: 'bg-gray-100 text-gray-900 hover:bg-gray-200'
}

const sizeClasses: Record<NonNullable<ButtonProps['size']>, string> = {
	sm: 'h-8 px-3 text-sm',
	md: 'h-10 px-4',
	lg: 'h-12 px-6 text-lg'
}

export function Button({ className, children, variant = 'default', size = 'md', ...props }: ButtonProps) {
	return (
		<button
			className={clsx(
				'inline-flex items-center justify-center rounded-md font-medium transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2',
				variantClasses[variant],
				sizeClasses[size],
				className
			)}
			{...props}
		>
			{children}
		</button>
	)
}