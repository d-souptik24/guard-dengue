/**
 * cn — Tailwind class merging utility
 * Combines clsx conditional logic with tailwind-merge deduplication.
 * Used across all GuardDengue UI components.
 */
import { clsx, type ClassValue } from 'clsx'
import { twMerge } from 'tailwind-merge'

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}
