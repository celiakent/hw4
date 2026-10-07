import { Link } from 'react-router-dom'

export default function About() {
  return (
    <div className="page narrow">
      <p className="eyebrow">About Us</p>
      <h1>Made for Bulldogs, right on Broadway.</h1>
      <p className="lead">
        Campus Customs runs Yale Bulldog Blue, a shop for officially licensed Yale apparel, a short
        walk from Old Campus at 57 Broadway in New Haven.
      </p>

      <h2>What we do</h2>
      <p>
        We make clothes that people actually wear around campus: soft hoodies, everyday crewnecks,
        tees for The Game, and warm quarter-zips for New Haven winters. Our designs cover Yale
        athletics, the graduate and professional schools, and the families who show up for every
        move-in day and Commencement.
      </p>

      <h2>Why we do it</h2>
      <p>
        A Yale sweatshirt goes with you to section, to the stands, and home for break. We want
        every piece to hold up for years, so we focus on solid fabrics, clean graphics, and fits
        that work for students and alumni alike.
      </p>

      <h2>Visit or get in touch</h2>
      <ul className="info-list">
        <li><strong>Store:</strong> 57 Broadway, New Haven, CT 06511</li>
        <li><strong>Orders &amp; questions:</strong> orderdept@campuscustoms.com, or use the chat in the corner</li>
        <li>
          <strong>Returns:</strong> Send unworn items with tags attached within 30 days of shipping.
          Final-sale and custom pieces can’t be returned.
        </li>
      </ul>

      <Link to="/products" className="btn">Shop the collection</Link>
    </div>
  )
}
