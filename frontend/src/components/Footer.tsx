import { Link } from 'react-router-dom'

export default function Footer() {
  return (
    <footer className="footer">
      <div className="footer-inner">
        <div>
          <strong>Campus Customs</strong>
          <p>Yale Bulldog Blue · Officially licensed</p>
          <p>57 Broadway, New Haven, CT 06511</p>
        </div>
        <div>
          <strong>Shop</strong>
          <p><Link to="/products">All products</Link></p>
          <p><Link to="/about">About us</Link></p>
        </div>
        <div>
          <strong>Help</strong>
          <p>orderdept@campuscustoms.com</p>
          <p>Returns accepted within 30 days of shipping</p>
        </div>
      </div>
      <p className="footer-fine">© 2026 Campus Customs. Boola Boola.</p>
    </footer>
  )
}
