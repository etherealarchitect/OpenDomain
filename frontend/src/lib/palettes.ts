export interface Palette {
  name: string;
  description: string;
  ground: string;
  groundRaised: string;
  groundOverlay: string;
  ink: string;
  inkDim: string;
  inkFaint: string;
  edge: string;
  focus: string;
  focusDim: string;
  live: string;
  liveDim: string;
  caution: string;
  fault: string;
}

export const PALETTES: Record<string, Palette> = {
  terminal: {
    name: "Terminal",
    description: "Dark zinc with blue accent — the default",
    ground: "#0c0c0e",
    groundRaised: "#141416",
    groundOverlay: "#1c1c20",
    ink: "#e4e4e7",
    inkDim: "#a1a1aa",
    inkFaint: "#52525b",
    edge: "#2a2a2e",
    focus: "#6d8aff",
    focusDim: "#6d8aff33",
    live: "#34d399",
    liveDim: "#34d39933",
    caution: "#fbbf24",
    fault: "#f87171",
  },

  signal: {
    name: "Signal",
    description: "Warm amber on dark parchment",
    ground: "#110f0b",
    groundRaised: "#1a1710",
    groundOverlay: "#231f17",
    ink: "#e8e0d0",
    inkDim: "#a89e8c",
    inkFaint: "#6b6355",
    edge: "#302a20",
    focus: "#e0a040",
    focusDim: "#e0a04033",
    live: "#7ec87e",
    liveDim: "#7ec87e33",
    caution: "#d4a84a",
    fault: "#d06050",
  },

  phosphor: {
    name: "Phosphor",
    description: "Green-on-black retro CRT",
    ground: "#0a0e0a",
    groundRaised: "#0f150f",
    groundOverlay: "#151e15",
    ink: "#b8e6b8",
    inkDim: "#6faa6f",
    inkFaint: "#3d6b3d",
    edge: "#1e2e1e",
    focus: "#4adf4a",
    focusDim: "#4adf4a33",
    live: "#4adf4a",
    liveDim: "#4adf4a33",
    caution: "#d4cc44",
    fault: "#e05050",
  },

  midnight: {
    name: "Midnight",
    description: "Deep navy with cyan highlights",
    ground: "#080c14",
    groundRaised: "#0e1420",
    groundOverlay: "#151d2c",
    ink: "#c8d6e8",
    inkDim: "#7a90aa",
    inkFaint: "#4a5e78",
    edge: "#1e2a3c",
    focus: "#38bdf8",
    focusDim: "#38bdf833",
    live: "#2dd4bf",
    liveDim: "#2dd4bf33",
    caution: "#facc15",
    fault: "#fb7185",
  },

  infrared: {
    name: "Infrared",
    description: "Dark charcoal with hot red-orange",
    ground: "#100808",
    groundRaised: "#181010",
    groundOverlay: "#221818",
    ink: "#e8d8d4",
    inkDim: "#aa8a84",
    inkFaint: "#6b5450",
    edge: "#302020",
    focus: "#f06040",
    focusDim: "#f0604033",
    live: "#4ace8a",
    liveDim: "#4ace8a33",
    caution: "#f0b040",
    fault: "#f04040",
  },

  clearnet: {
    name: "Clearnet",
    description: "Light mode — clean and bright",
    ground: "#f8f8fa",
    groundRaised: "#ffffff",
    groundOverlay: "#eeeff2",
    ink: "#1a1a2e",
    inkDim: "#5c5c72",
    inkFaint: "#9898a8",
    edge: "#dcdce4",
    focus: "#3b5ccc",
    focusDim: "#3b5ccc1a",
    live: "#1a8a50",
    liveDim: "#1a8a501a",
    caution: "#b07818",
    fault: "#c03030",
  },
};

export const PALETTE_KEYS = Object.keys(PALETTES) as (keyof typeof PALETTES)[];

export const STORAGE_KEY = "opendomain-palette";

export function applyPalette(key: string) {
  const palette = PALETTES[key] ?? PALETTES.terminal;
  const root = document.documentElement;
  root.style.setProperty("--color-ground", palette.ground);
  root.style.setProperty("--color-ground-raised", palette.groundRaised);
  root.style.setProperty("--color-ground-overlay", palette.groundOverlay);
  root.style.setProperty("--color-ink", palette.ink);
  root.style.setProperty("--color-ink-dim", palette.inkDim);
  root.style.setProperty("--color-ink-faint", palette.inkFaint);
  root.style.setProperty("--color-edge", palette.edge);
  root.style.setProperty("--color-focus", palette.focus);
  root.style.setProperty("--color-focus-dim", palette.focusDim);
  root.style.setProperty("--color-live", palette.live);
  root.style.setProperty("--color-live-dim", palette.liveDim);
  root.style.setProperty("--color-caution", palette.caution);
  root.style.setProperty("--color-fault", palette.fault);
  localStorage.setItem(STORAGE_KEY, key);
}

export function getStoredPalette(): string {
  if (typeof window === "undefined") return "terminal";
  return localStorage.getItem(STORAGE_KEY) ?? "terminal";
}
