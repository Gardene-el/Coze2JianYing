import { create } from 'zustand'

interface TourState {
  open: boolean
}

interface TourActions {
  startTour: () => void
  closeTour: () => void
}

type TourStore = TourState & TourActions

export const useTourStore = create<TourStore>()((set) => ({
  open: false,
  startTour: () => set({ open: true }),
  closeTour: () => set({ open: false }),
}))
