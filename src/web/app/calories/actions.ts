'use server';

import { revalidatePath } from 'next/cache';

const API_URL = process.env.API_URL || 'http://localhost:3001';

export type FoodEntry = {
  id: number;
  name: string;
  calories: number;
  logged_at: string;
};

export async function getFoodEntries(): Promise<FoodEntry[]> {
  const res = await fetch(`${API_URL}/food-entries`, { cache: 'no-store' });
  if (!res.ok) throw new Error('Failed to fetch food entries');
  return res.json();
}

export async function createFoodEntry(formData: FormData) {
  const name = formData.get('name') as string;
  const calories = formData.get('calories') as string;
  await fetch(`${API_URL}/food-entries`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ name, calories: Number(calories) }),
  });
  revalidatePath('/calories');
}

export async function deleteFoodEntry(id: number) {
  await fetch(`${API_URL}/food-entries/${id}`, { method: 'DELETE' });
  revalidatePath('/calories');
}
