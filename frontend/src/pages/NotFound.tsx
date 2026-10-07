import { Link } from 'react-router-dom'

export default function NotFound() {
  return (
    <div className="page narrow">
      <h1>Page not found</h1>
      <p>That page wandered off campus.</p>
      <Link to="/" className="btn">Back to home</Link>
    </div>
  )
}
