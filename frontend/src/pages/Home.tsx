import { useEffect, useRef, useState } from 'react'
import { Link } from 'react-router-dom'
import { getProducts, type Product } from '../api'
import ProductCard from '../components/ProductCard'
import { COLLECTIONS } from '../collections'

const FEATURED_IDS = [
  '2025-yale-vs-harvard-t-shirt',
  'baseball-left-chest-crewneck',
  'ice-hockey-left-chest-hoodie',
  'yale-mom-hoodie',
]

export default function Home() {
  const [featured, setFeatured] = useState<Product[]>([])
  const innerRef = useRef<HTMLDivElement>(null)
  const mediaRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    getProducts()
      .then((all) => {
        const picks = FEATURED_IDS.map((id) => all.find((p) => p.product_id === id)).filter(
          (p): p is Product => Boolean(p),
        )
        setFeatured(picks.length ? picks : all.slice(0, 4))
      })
      .catch(() => setFeatured([]))
  }, [])

  // Acme-style hero on scroll: the text drifts down and fades out, and the photo
  // parallaxes slightly, as you scroll past the first screen.
  useEffect(() => {
    let raf = 0
    const onScroll = () => {
      raf = requestAnimationFrame(() => {
        const y = window.scrollY
        const vh = window.innerHeight || 1
        const p = Math.min(y / (vh * 0.75), 1)
        if (innerRef.current) {
          innerRef.current.style.transform = `translateY(${y * 0.35}px)`
          innerRef.current.style.opacity = String(1 - p)
        }
        if (mediaRef.current) {
          mediaRef.current.style.transform = `translateY(${y * 0.15}px)`
        }
      })
    }
    window.addEventListener('scroll', onScroll, { passive: true })
    return () => {
      window.removeEventListener('scroll', onScroll)
      cancelAnimationFrame(raf)
    }
  }, [])

  return (
    <>
      <section className="hero">
        <div className="hero-media" ref={mediaRef}>
          <img src="/yale-campus-hero.jpg" alt="Yale campus" />
        </div>
        <div className="hero-inner" ref={innerRef}>
          <h1>Campus Customs</h1>
          <p>Officially licensed Yale apparel.</p>
          <Link to="/products" className="btn">Shop</Link>
        </div>
      </section>

      <section className="page">
        <h2 className="section-title">Collections</h2>
        <div className="collections">
          {COLLECTIONS.map((c) => (
            <Link key={c.slug} to={`/products?collection=${c.slug}`} className="collection-card">
              <h3>{c.title}</h3>
            </Link>
          ))}
        </div>

        <h2 className="section-title">Featured</h2>
        <div className="product-grid">
          {featured.map((p) => (
            <ProductCard key={p.product_id} product={p} />
          ))}
        </div>
      </section>
    </>
  )
}
