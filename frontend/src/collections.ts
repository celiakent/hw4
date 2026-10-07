export interface Collection {
  slug: string
  title: string
  blurb: string
  keywords: string[]
}

// A product belongs to a collection if any keyword appears in its name, type, or tags.
export const COLLECTIONS: Collection[] = [
  {
    slug: 'layers',
    title: 'Hoodies',
    blurb: 'Hoodies, crewnecks, and sweatshirts.',
    keywords: ['hoodie', 'crewneck', 'sweatshirt'],
  },
  {
    slug: 'game-day',
    title: 'Game Day',
    blurb: 'Gear for nearly every varsity sport.',
    keywords: ['sport', 'baseball', 'hockey', 'football', 'soccer', 'tennis', 'golf', 'swimming', 'diving', 'volleyball', 'the game'],
  },
  {
    slug: 'family',
    title: 'Family',
    blurb: 'Mom, Dad, Grandpa, and more.',
    keywords: ['mom', 'dad', 'grandma', 'grandpa', 'aunt', 'uncle'],
  },
]
