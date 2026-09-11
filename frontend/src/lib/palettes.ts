export interface Palette {
  name: string;
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

  clearnet: {
    name: "Clearnet",
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
