/// <reference types="vitest" />
import { render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import App from './App'

test('renders welcome page', () => {
  render(
    <MemoryRouter initialEntries={['/']}>
      <App />
    </MemoryRouter>
  )
  expect(screen.getByText('Welcome to Agnes AI')).toBeInTheDocument()
})

test('renders edit image page', () => {
  render(
    <MemoryRouter initialEntries={['/edit']}>
      <App />
    </MemoryRouter>
  )
  expect(screen.getByText('Upload Image')).toBeInTheDocument()
  expect(screen.getByText('Generate')).toBeInTheDocument()
})
