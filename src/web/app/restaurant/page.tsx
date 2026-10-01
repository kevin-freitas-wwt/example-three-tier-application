import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Riverside Burger Co.",
  description: "A neighborhood burger restaurant serving fresh, local burgers daily.",
};

const menu = [
  {
    name: "The Classic",
    description: "Beef patty, cheddar, lettuce, tomato, house sauce",
    price: "$9.50",
  },
  {
    name: "Bacon Smash",
    description: "Double patty, crispy bacon, caramelized onions, smoked gouda",
    price: "$12.00",
  },
  {
    name: "Veggie Delight",
    description: "Grilled portobello & black bean patty, avocado, chipotle mayo",
    price: "$10.00",
  },
  {
    name: "Spicy Jalapeño",
    description: "Beef patty, pepper jack, jalapeños, chipotle aioli",
    price: "$10.50",
  },
];

const hours = [
  { day: "Monday – Thursday", time: "11:00 AM – 9:00 PM" },
  { day: "Friday – Saturday", time: "11:00 AM – 10:00 PM" },
  { day: "Sunday", time: "12:00 PM – 8:00 PM" },
];

export default function RestaurantHome() {
  return (
    <div className="min-h-screen bg-amber-50 dark:bg-zinc-900">
      {/* Hero */}
      <header className="bg-amber-600 dark:bg-amber-800 text-white py-16 px-4 text-center">
        <h1 className="text-4xl sm:text-5xl font-extrabold tracking-tight">
          🍔 Riverside Burger Co.
        </h1>
        <p className="mt-4 text-lg sm:text-xl text-amber-50">
          Fresh, local, and flipped with love — right in your neighborhood.
        </p>
      </header>

      <main className="max-w-3xl mx-auto px-4 py-12 space-y-16">
        {/* Menu */}
        <section aria-labelledby="menu-heading">
          <h2
            id="menu-heading"
            className="text-2xl font-bold text-zinc-900 dark:text-zinc-50 mb-6"
          >
            Our Menu
          </h2>
          <ul className="space-y-4">
            {menu.map((item) => (
              <li
                key={item.name}
                className="flex items-start justify-between gap-4 rounded-lg border border-amber-200 dark:border-zinc-700 bg-white dark:bg-zinc-800 px-5 py-4"
              >
                <div>
                  <p className="font-semibold text-zinc-900 dark:text-zinc-50">
                    {item.name}
                  </p>
                  <p className="text-sm text-zinc-600 dark:text-zinc-300">
                    {item.description}
                  </p>
                </div>
                <span className="font-semibold text-amber-700 dark:text-amber-400 whitespace-nowrap">
                  {item.price}
                </span>
              </li>
            ))}
          </ul>
        </section>

        {/* Hours */}
        <section aria-labelledby="hours-heading">
          <h2
            id="hours-heading"
            className="text-2xl font-bold text-zinc-900 dark:text-zinc-50 mb-6"
          >
            Hours
          </h2>
          <ul className="space-y-2">
            {hours.map((entry) => (
              <li
                key={entry.day}
                className="flex items-center justify-between rounded-lg bg-white dark:bg-zinc-800 border border-amber-200 dark:border-zinc-700 px-5 py-3"
              >
                <span className="text-zinc-800 dark:text-zinc-100">{entry.day}</span>
                <span className="text-zinc-600 dark:text-zinc-300">{entry.time}</span>
              </li>
            ))}
          </ul>
        </section>

        {/* Location */}
        <section aria-labelledby="location-heading">
          <h2
            id="location-heading"
            className="text-2xl font-bold text-zinc-900 dark:text-zinc-50 mb-6"
          >
            Find Us
          </h2>
          <div className="rounded-lg bg-white dark:bg-zinc-800 border border-amber-200 dark:border-zinc-700 px-5 py-4 text-zinc-700 dark:text-zinc-200">
            <p className="font-semibold text-zinc-900 dark:text-zinc-50">
              Riverside Burger Co.
            </p>
            <p>123 Maple Street, Springfield</p>
            <p>(555) 867-5309</p>
          </div>
        </section>
      </main>

      <footer className="text-center text-sm text-zinc-500 dark:text-zinc-400 py-8">
        © {new Date().getFullYear()} Riverside Burger Co. All rights reserved.
      </footer>
    </div>
  );
}
