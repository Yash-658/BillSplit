import { useState } from "react";
import { AssignScreen } from "./components/AssignScreen";
import { Layout } from "./components/Layout";
import { ResultsScreen } from "./components/ResultsScreen";
import { ReviewScreen } from "./components/ReviewScreen";
import { UploadScreen } from "./components/UploadScreen";
import { mockBill } from "./data/mockBill";
import type { Assignment, Bill, CalculateResult, Stage } from "./types";

const initialAssignments: Assignment = {
  biryani: ["Yash"],
  naan: ["Yash", "Rahul"],
  paneer: ["Rahul"],
  coke: ["everyone"],
};

function App() {
  const [stage, setStage] = useState<Stage>("upload");
  const [bill, setBill] = useState<Bill>(mockBill);
  const [people, setPeople] = useState(["Yash", "Rahul"]);
  const [assignments, setAssignments] = useState<Assignment>(initialAssignments);
  const [calculation, setCalculation] = useState<CalculateResult | null>(null);
  const startOver = () => { setStage("upload"); setBill(mockBill); setPeople(["Yash", "Rahul"]); setAssignments(initialAssignments); };
  return <Layout stage={stage}>
    {stage === "upload" && <UploadScreen onExtracted={(extractedBill) => { setBill(extractedBill); setAssignments({}); setStage("review"); }} />}
    {stage === "review" && <ReviewScreen bill={bill} setBill={setBill} onContinue={() => setStage("assign")} />}
    {stage === "assign" && <AssignScreen bill={bill} people={people} setPeople={setPeople} assignments={assignments} setAssignments={setAssignments} onBack={() => setStage("review")} onContinue={(result) => { setCalculation(result); setStage("results"); }} />}
    {stage === "results" && calculation && <ResultsScreen result={calculation} onBack={() => setStage("assign")} onStartOver={startOver} />}
  </Layout>;
}

export default App;
