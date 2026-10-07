import { Link, NavLink, useLocation, useNavigate } from 'react-router-dom'
import { useAuth } from '../auth'

const linkClass = ({ isActive }: { isActive: boolean }) =>
  isActive ? 'nav-link active' : 'nav-link'

export default function NavBar() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()
  const overlay = location.pathname === '/'

  async function handleLogout() {
    await logout()
    navigate('/')
  }

  return (
    <header className={`site-header${overlay ? ' overlay' : ''}`}>
      <nav className="nav">
        <Link to="/" className="brand">
          <span className="brand-mark">CC</span>
          <span className="brand-text">Campus Customs</span>
        </Link>
        <ul className="nav-links">
          <li><NavLink to="/" end className={linkClass}>Home</NavLink></li>
          <li><NavLink to="/products" className={linkClass}>Shop</NavLink></li>
          <li><NavLink to="/about" className={linkClass}>About</NavLink></li>
        </ul>
        <div className="nav-account">
          {user ? (
            <>
              <span className="nav-greeting">{user.first_name}</span>
              <button type="button" className="nav-link" onClick={handleLogout}>Log out</button>
            </>
          ) : (
            <>
              <NavLink to="/login" className={linkClass}>Log in</NavLink>
              <NavLink to="/signup" className={linkClass}>Sign up</NavLink>
            </>
          )}
        </div>
      </nav>
    </header>
  )
}
