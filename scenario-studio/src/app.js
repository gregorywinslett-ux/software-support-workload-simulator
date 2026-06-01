/* Scenario Studio: dependency-free prototype with typed JSDoc models. */

/**
 * @typedef {{id:string,name:string,role?:string}} Participant
 * @typedef {{id:string,text:string,scores:Record<string,number>,selected?:boolean}} FocalQuestion
 * @typedef {{id:string,title:string,description:string,category:string,notes:string,evidence:string}} DrivingForce
 * @typedef {{label:string,description:string,visible:string,plausible:string}} PlausibleExtreme
 * @typedef {{id:string,name:string,description:string,forceIds:string[],causalNotes:string,openQuestions:string,extremes:{a:PlausibleExtreme,b:PlausibleExtreme},impact:number,uncertainty:number,impactWins:number,uncertaintyWins:number}} Cluster
 * @typedef {{clusterId:string,low:string,high:string,reversed?:boolean}} ScenarioAxis
 * @typedef {{id:string,name:string,descriptor:string,icon:string,quadrant:number,fields:Record<string,string>,events:TimelineEvent[],critiques:CritiqueNote[]}} Scenario
 * @typedef {{id:string,title:string,year:string,description:string,cause:string,consequence:string,stakeholders:string,signal:string,plausibility:string}} TimelineEvent
 * @typedef {{id:string,text:string,status:"accepted"|"edited"|"parked"|"rejected"}} CritiqueNote
 * @typedef {{id:string,title:string,description:string,owner:string,timeframe:string,effort:number,confidence:number,ratings:Record<string,string>,classification:string}} StrategicAction
 * @typedef {{scenarioId:string,fitScore:number,riskScore:number,workloadBurden:number,confidence:number,strategicValue:number,reversibility:number,resultLabel:string,whatHappens:string,keyRisks:string,adaptationNeeded:string,conditionsForSuccess:string,earlyWarningSignals:string,notes:string}} StressTestScenarioResult
 * @typedef {{id:string,actionTitle:string,actionDescription:string,actionType:string,owner:string,timeframe:string,createdAt:string,scenarioResults:StressTestScenarioResult[],overallClassification:string,suggestedClassification:string,overallNotes:string,adaptationSummary:string,decisionRecommendation:string}} StrategicStressTest
 * @typedef {{id:string,date:string,strength:string,confidence:string,direction:string,evidence:string,notes:string}} WeakSignalHistoryEntry
 * @typedef {{id:string,title:string,description:string,linkedScenarioIds:string[],category:string,currentStrength:string,confidence:string,direction:string,evidence:string,source:string,owner:string,reviewCadence:string,lastReviewed:string,nextReview:string,notes:string,history:WeakSignalHistoryEntry[]}} WeakSignal
 * @typedef {{id:string,step:number,text:string,createdAt:string}} DecisionLogEntry
 * @typedef {{id:string,text:string,sourceStep:number,createdAt:string}} ParkingLotItem
 */

const STATE_VERSION = 3;
const STORAGE_KEY = "scenario-studio-state-v3";
const LEGACY_STORAGE_KEYS = ["scenario-studio-state-v2", "scenario-studio-state-v1"];
const $ = (selector, root = document) => root.querySelector(selector);
const $$ = (selector, root = document) => Array.from(root.querySelectorAll(selector));
const uid = (prefix) => `${prefix}_${Math.random().toString(36).slice(2, 8)}${Date.now().toString(36).slice(-4)}`;

const steps = [
  ["Setup", "Frame the workshop and shared display."],
  ["Focal Question", "Craft the strategic question."],
  ["Driving Forces", "Capture forces shaping the future."],
  ["Clustering", "Group related forces into dynamic conditions."],
  ["Plausible Extremes", "Define two plausible outcomes for each cluster."],
  ["Prioritisation", "Identify the most important uncertainties."],
  ["Scenario Matrix", "Build the 2x2 scenario theatre."],
  ["Scenario Sketches", "Develop each quadrant."],
  ["Storylines", "Create causal timelines."],
  ["Critique", "Challenge and strengthen scenarios."],
  ["Strategic Implications", "Test actions across futures."],
  ["Stress-Test Theatre", "Put strategies under the lights."],
  ["Weak Signals Monitor", "Track which futures may be emerging."],
  ["Export", "Produce useful artefacts."],
];

const categories = [
  "Political / policy", "Economic / funding", "Social / cultural", "Technological",
  "Legal / regulatory", "Environmental", "Organisational", "Workforce",
  "Student expectations", "Pedagogical", "Other"
];

const prompts = {
  0: ["Set the room expectation: this is exploration, not prediction.", "Invite participants to keep choices-now in view."],
  1: ["Is the question too broad?", "Is there a clear time horizon?", "Does it connect to real choices?", "Is it framed as exploration rather than prediction?"],
  2: ["What might change in student expectations?", "What might change in staff capability?", "What might change in regulation?", "What might become harder to sustain?", "What might disrupt the current operating model?"],
  3: ["Name clusters as dynamic conditions, not static topics.", "Ask what forces move together and why.", "Keep useful but out-of-scope material parked."],
  4: ["Are both outcomes plausible?", "Are they structurally different?", "Are they more than simply good versus bad?"],
  5: ["Critical uncertainties should be high impact and high uncertainty.", "Pairwise comparison can reveal what the room is really privileging."],
  6: ["Do these axes create four genuinely different futures?", "Are the axes independent enough?", "Is any quadrant implausible?"],
  7: ["Make the scenario concrete enough to reason inside.", "Balance risks, opportunities, winners and losers."],
  8: ["What happens first?", "What accelerates change?", "What resists change?", "What becomes visible too late?"],
  9: ["What feels too neat or linear?", "What actor is missing?", "What would make this more uncomfortable?", "Is this distinct from the others?"],
  10: ["Which actions are robust across futures?", "What should be delayed until a signal appears?", "What should be stopped now?"],
  11: ["Put one strategy under the lights.", "Ask what changes in each future.", "Look for adaptations, not just approval."],
  12: ["What signals would tell us a scenario is emerging?", "What has changed since last review?", "Which actions need attention if this signal strengthens?"],
  13: ["Export the narrative while decisions are still fresh.", "Print to PDF for a stable workshop artefact."],
};

const stepGuides = [
  {
    plain: "We are setting the boundaries for the conversation so the workshop has a clear future question, audience and time horizon.",
    why: "Scenario thinking works best when the group explores one focused issue rather than trying to discuss the whole future.",
    example: "Instead of “AI in education”, use “How might digital teaching support needs evolve by 2029?”",
    good: ["The issue is specific enough to discuss.", "The time horizon is far enough for uncertainty.", "The output connects to choices now."],
    trap: "Starting too broad makes every later decision feel vague.",
    reassurance: "It is fine if the wording is imperfect now. Step 1 sharpens it.",
  },
  {
    plain: "We are turning the broad issue into a strong focal question for the whole workshop.",
    why: "The focal question becomes the anchor for deciding which forces matter, which uncertainties are critical and which actions are useful.",
    example: "Strong: “How might digital teaching support needs evolve by 2029, and what would this mean for service design?”",
    good: ["It asks about an uncertain future.", "It is connected to real decisions.", "It is neither too broad nor too narrow."],
    trap: "A prediction question like “What will happen?” can make the group search for one answer instead of several plausible futures.",
    reassurance: "Scoring is not a test. It simply helps the room see which wording is most useful.",
  },
  {
    plain: "We are collecting forces of change: things outside or around us that could shape the future.",
    why: "Good scenarios are built from forces, not just opinions or preferred solutions.",
    example: "Force: “Academic staff expect just-in-time support.” Not a force: “We need better training.”",
    good: ["Forces describe change or pressure.", "They can plausibly affect the focal question.", "They are concrete enough to discuss."],
    trap: "Capturing solutions too early narrows the conversation before the future has been explored.",
    reassurance: "This step is meant to feel abundant and a little messy.",
  },
  {
    plain: "We are grouping related forces into dynamic conditions that could move in different directions.",
    why: "Clusters reduce noise and reveal the bigger uncertainties underneath the raw ideas.",
    example: "Weak: “AI”. Strong: “Institutional confidence in AI-enabled teaching”.",
    good: ["Cluster names describe a condition that can vary.", "Forces in the cluster have a causal relationship.", "Useful outliers are parked, not lost."],
    trap: "Using topic labels creates folders, not scenario-building material.",
    reassurance: "Clustering is usually the messiest step. That is normal.",
  },
  {
    plain: "For each cluster, we are defining two different but plausible ways that condition could unfold.",
    why: "These extremes give the group material for building scenario axes and distinct futures.",
    example: "Instead of “good AI” vs “bad AI”, use “coordinated adoption with trusted guardrails” vs “fragmented caution and local workarounds”.",
    good: ["Both outcomes are plausible.", "They are structurally different.", "They are not simply optimistic and pessimistic versions."],
    trap: "Making one side obviously desirable and the other obviously terrible weakens the scenarios.",
    reassurance: "Plausible does not mean likely. It means worth preparing for.",
  },
  {
    plain: "We are deciding which uncertainties matter most for the focal question.",
    why: "The two most important and uncertain clusters become the axes for the scenario matrix.",
    example: "High impact: it would change service design. High uncertainty: we genuinely do not know which way it will go.",
    good: ["Impact and uncertainty are judged separately.", "The room can explain why the top uncertainties matter.", "Overrides are deliberate, not accidental."],
    trap: "Choosing what feels most important but is already predictable will produce flat scenarios.",
    reassurance: "The matrix is a decision aid, not a mathematical truth machine.",
  },
  {
    plain: "We are combining two critical uncertainties to create four different scenario spaces.",
    why: "Each quadrant gives the group a different operating environment to explore before choosing actions.",
    example: "One quadrant might combine high AI confidence with low staff capacity, producing automation without absorption.",
    good: ["Each quadrant combines one endpoint from each axis.", "The four futures feel meaningfully different.", "The axes are not just best-case/worst-case."],
    trap: "Reading the matrix as a prediction or preference ranking misses the point.",
    reassurance: "We are not choosing the future we want. We are building futures to think with.",
  },
  {
    plain: "We are making each scenario concrete enough that people can reason inside it.",
    why: "A scenario name alone is not useful. The group needs to feel what changes, who benefits and what becomes harder.",
    example: "“In this future, support demand feels urgent, uneven and increasingly tied to AI-enabled assessment choices.”",
    good: ["The scenario is vivid but not over-written.", "Risks and opportunities both appear.", "Early signs are visible."],
    trap: "Writing a strategy instead of describing the operating environment.",
    reassurance: "Short, vivid sketches are enough at this stage.",
  },
  {
    plain: "We are turning each scenario into a causal story over time.",
    why: "Storylines make scenarios more plausible by showing how change could unfold, accelerate or stall.",
    example: "Because policy confidence improved, faculties adopted shared tools, which changed the demand for support.",
    good: ["Events have causes and consequences.", "There are signals the organisation could monitor.", "The story includes resistance as well as momentum."],
    trap: "Listing events without explaining why one thing leads to another.",
    reassurance: "The aim is a believable chain, not a perfect forecast.",
  },
  {
    plain: "We are stress-testing the scenarios before using them for strategic choices.",
    why: "Critique makes scenarios harder to dismiss and more useful for decision-making.",
    example: "Ask: “What actor is missing?” or “What assumption makes this scenario too neat?”",
    good: ["Critiques are treated as improvements.", "Weak assumptions are made visible.", "Scenarios become more distinct."],
    trap: "Treating critique as negativity or reopening every decision.",
    reassurance: "Strong scenarios get better when challenged.",
  },
  {
    plain: "We are testing possible actions against all four futures.",
    why: "This separates robust actions from actions that only work if one narrow future comes true.",
    example: "Robust: reusable support patterns. Contingent: major platform investment only if integration improves.",
    good: ["Actions are rated against every scenario.", "Owners and next decisions are captured.", "Monitoring signals are linked to deferred choices."],
    trap: "Jumping to favourite actions without testing them across futures.",
    reassurance: "The best action is not always the boldest. Sometimes it is the one that keeps options open.",
  },
  {
    plain: "We are putting one proposed strategy under the lights and asking how it behaves in each scenario.",
    why: "A strategy may look sensible in today's world but become fragile, risky or powerful under different futures.",
    example: "A central AI teaching support hub may be robust in coordinated acceleration but overloaded in automation without absorption.",
    good: ["Each scenario has a clear fit/risk judgement.", "Adaptations and success conditions are captured.", "The recommendation is transparent and editable."],
    trap: "Treating this as a pass/fail vote rather than a structured adaptation conversation.",
    reassurance: "The theatre is meant to reveal what would need to change, not embarrass an idea.",
  },
  {
    plain: "We are turning scenarios into a living sensing system by tracking weak signals over time.",
    why: "Weak signals help the group notice which future may be becoming more active before it is obvious.",
    example: "Repeated urgent AI support requests may suggest automation is moving faster than staff capacity.",
    good: ["Signals are linked to scenarios.", "Evidence and confidence are recorded.", "Review dates make monitoring actionable."],
    trap: "Tracking vague anecdotes without evidence, owner or review cadence.",
    reassurance: "Signals can be faint. The point is to watch their direction, not prove certainty.",
  },
  {
    plain: "We are turning the workshop into artefacts people can use after the room disperses.",
    why: "The value of the workshop depends on whether scenarios, signals and actions can be shared and revisited.",
    example: "Use the report for the record, the presentation summary for briefings and the signals dashboard for monitoring.",
    good: ["The report is understandable to non-attendees.", "Actions have owners or next decisions.", "Signals are clear enough to revisit later."],
    trap: "Ending with interesting scenarios but no follow-through.",
    reassurance: "This is where the conversation becomes organisational memory.",
  },
];

const glossary = [
  ["Driving force", "A change, pressure or trend that could shape the future."],
  ["Cluster", "A group of related forces named as a dynamic condition that could move in different directions."],
  ["Critical uncertainty", "A cluster that is both highly important and genuinely uncertain."],
  ["Plausible extreme", "One possible endpoint for how an uncertainty could unfold. It must be believable, not necessarily likely."],
  ["Scenario axis", "A critical uncertainty used to structure the 2x2 matrix."],
  ["Scenario", "A plausible future operating environment, not a prediction or preferred plan."],
  ["Early warning indicator", "A signal that suggests one future may be becoming more likely."],
  ["Robust action", "An action that remains useful across several different scenarios."],
  ["Hedging action", "A low-cost action that preserves options while uncertainty remains."],
];

const transformation = ["Setup", "Question", "Forces", "Clusters", "Extremes", "Axes", "Scenarios", "Storylines", "Critique", "Actions", "Stress test", "Signals", "Export"];

const stressActionTypes = ["Strategy", "Initiative", "Policy", "Service change", "Investment", "Pilot", "Stop doing", "Other"];
const stressLabels = ["Strong fit", "Useful but adapt", "High risk", "Fragile", "Unclear", "Poor fit"];
const stressClassifications = ["Robust", "Contingent", "Fragile", "High upside / high risk", "Worth piloting", "Monitor only", "Stop or avoid"];
const stressRecommendations = ["Proceed now", "Proceed with adaptation", "Pilot first", "Hold and monitor", "Do not proceed"];
const signalCategories = ["Staff behaviour", "Student behaviour", "Policy / regulation", "Technology", "Workload / capacity", "Service demand", "Financial / resourcing", "Risk / compliance", "Sector movement", "Stakeholder sentiment", "Other"];
const signalStrengths = ["Not visible", "Faint", "Emerging", "Strong", "Critical"];
const signalConfidences = ["Low", "Medium", "High"];
const signalDirections = ["Increasing", "Stable", "Decreasing", "Unknown"];
const reviewCadences = ["Weekly", "Fortnightly", "Monthly", "Quarterly", "Ad hoc"];

let state = loadState() || createEmptyWorkshop();
let draggedForceId = null;
let draggedEventId = null;
let activeScenarioId = null;
let timerSeconds = 20 * 60;
let timerHandle = null;
let undoStack = [];

function createEmptyWorkshop() {
  const scenarios = ["North West", "North East", "South West", "South East"].map((name, i) => ({
    id: uid("scenario"),
    name,
    descriptor: "",
    icon: ["Compass", "Signal", "Anchor", "Spark"][i],
    quadrant: i,
    fields: {},
    events: [],
    critiques: [],
  }));
	  return {
    version: STATE_VERSION,
	    currentStep: 0,
    ui: { roomMode: false, exportView: "report", guidedMode: true, glossaryOpen: false },
    setup: {
      title: "Scenario Studio Workshop",
      organisation: "",
      date: new Date().toISOString().slice(0, 10),
      facilitator: "",
      participants: "",
      focalIssue: "",
      timeHorizon: "2029",
      desiredOutput: "A set of plausible scenarios and robust strategic actions.",
      openingStatement: "Today we are exploring:\nHow might [focal issue] evolve by [time horizon], and what would this mean for our choices now?",
    },
    focalQuestions: [],
    drivingForces: [],
    clusters: [],
    axes: { x: null, y: null },
    scenarios,
    actions: [],
    stressTests: [],
    weakSignals: [],
    signalFilters: { scenario: "All", category: "All", strength: "All", confidence: "All", direction: "All", reviewDue: false, sort: "strongest" },
	    parkingLot: [],
	    decisionLog: [],
    implications: { start: "", stop: "", protect: "", monitor: "", decideNow: "", defer: "" },
    minorityReports: [],
	    pairwise: { impact: [], uncertainty: [], cursorImpact: 0, cursorUncertainty: 0 },
    savedAt: null,
	  };
	}

function sampleWorkshop() {
  const s = createEmptyWorkshop();
  s.setup = {
    title: "Digital Teaching Support Futures",
    organisation: "Large University",
    date: "2026-06-01",
    facilitator: "Scenario Studio Facilitator",
    participants: "Learning designers, academic leaders, professional services, student representatives",
    focalIssue: "digital teaching support needs at a large university",
    timeHorizon: "2029",
    desiredOutput: "Scenario matrix, early warning indicators and strategic service design actions.",
    openingStatement: "Today we are exploring:\nHow might digital teaching support needs at a large university evolve by 2029, and what would this mean for service design?",
  };
  s.focalQuestions = [{
    id: uid("fq"),
    text: "How might digital teaching support needs at a large university evolve by 2029, and what would this mean for service design?",
    selected: true,
    scores: { relevance: 5, uncertainty: 5, scope: 4, actionability: 5, usefulness: 5 },
  }];
  const forceTitles = [
    "Generative AI becomes ordinary in teaching preparation.",
    "Assessment integrity expectations increase.",
    "Staff workload limits capacity for redesign.",
    "Students expect more flexible and personalised learning support.",
    "Central systems become more integrated but harder to customise.",
    "Faculties develop uneven local support models.",
    "Regulatory scrutiny of online learning increases.",
    "Demand for learning analytics grows.",
    "Budget constraints intensify.",
    "Academic staff expect just-in-time support rather than formal training.",
    "Digital accessibility expectations rise.",
    "Vendor platforms add more embedded AI features.",
    "Teaching teams become more distributed.",
    "Professional staff roles become more strategically important.",
    "Demand for evidence of teaching quality increases.",
  ];
  const cats = ["Technological", "Legal / regulatory", "Workforce", "Student expectations", "Technological", "Organisational", "Legal / regulatory", "Pedagogical", "Economic / funding", "Workforce", "Legal / regulatory", "Technological", "Organisational", "Workforce", "Pedagogical"];
  s.drivingForces = forceTitles.map((title, i) => ({ id: uid("force"), title, description: "A workshop input shaping future digital teaching support needs.", category: cats[i], notes: "", evidence: "" }));
  const clusterNames = [
    "Institutional confidence in AI-enabled teaching",
    "Staff capacity to absorb teaching change",
    "Coherence of the digital learning ecosystem",
    "Student expectations for flexibility and support",
    "Regulatory and quality assurance pressure",
    "Faculty variation in local support models",
    "Availability of evidence and analytics",
    "Sustainability of central support capacity",
  ];
  s.clusters = clusterNames.map((name, i) => makeCluster(name, s.drivingForces.filter((_, idx) => idx % clusterNames.length === i).map(f => f.id)));
  s.clusters[0].extremes = {
    a: { label: "Low confidence and fragmented caution", description: "Adoption is local, cautious and uneven.", visible: "Policy ambiguity, shadow practices and pilot fatigue.", plausible: "Risk appetite differs across faculties and disciplines." },
    b: { label: "High confidence and coordinated adoption", description: "AI-enabled teaching is governed, supported and widely adopted.", visible: "Clear patterns, shared tools and practical support.", plausible: "Leaders invest in guardrails and professional support." },
  };
  s.clusters[1].extremes = {
    a: { label: "Low capacity with chronic overload", description: "Staff cannot absorb redesign demands.", visible: "Short-term fixes, exhausted teams and deferred quality work.", plausible: "Workload pressure continues to compound." },
    b: { label: "Strong capacity with protected time and practical support", description: "Teams have room and support to redesign teaching well.", visible: "Protected redesign windows and pragmatic service models.", plausible: "The university funds change capacity around priority programs." },
  };
  s.clusters.forEach((c, i) => { c.impact = i < 2 ? 5 : 3 + (i % 3); c.uncertainty = i < 2 ? 5 : 2 + (i % 4); });
  s.axes = {
    x: { clusterId: s.clusters[0].id, low: s.clusters[0].extremes.a.label, high: s.clusters[0].extremes.b.label, sync: true },
    y: { clusterId: s.clusters[1].id, low: s.clusters[1].extremes.a.label, high: s.clusters[1].extremes.b.label, sync: true },
  };
  const names = ["Coordinated Acceleration", "Automation Without Absorption", "Cautious Consolidation", "Exhausted Fragmentation"];
  s.scenarios.forEach((sc, i) => {
    sc.name = names[i];
    sc.descriptor = [
      "AI adoption and staff capacity reinforce each other in a coordinated improvement cycle.",
      "Tools proliferate faster than people can absorb the change.",
      "Measured adoption combines with practical staff support and quality assurance.",
      "Low confidence and low capacity create fragmented, reactive service demand.",
    ][i];
    sc.fields = {
      feel: "The organisation feels more explicit about trade-offs and capability.",
      changed: "Support demand shifts from tool training to service orchestration.",
      same: "Teaching quality still depends on local relationships and trust.",
      benefits: "Teams with clear priorities and shared services.",
      struggles: "Units relying on informal support or heroic individual effort.",
      easier: "Making visible service design choices.",
      harder: "Sustaining bespoke support for every local need.",
      risks: "Over-standardisation, under-investment and uneven adoption.",
      opportunities: "Reusable patterns, stronger evidence and clearer roles.",
      signs: "Policy updates, service queues, analytics demand and support escalations.",
    };
    sc.events = [
      { id: uid("event"), title: "Signals intensify", year: "2026", description: "Requests become more urgent and less uniform.", cause: "AI, workload and student expectations converge.", consequence: "Support teams redesign triage.", stakeholders: "Teaching teams, students, central support", signal: "More complex tickets and program-level requests.", plausibility: "Already visible in many universities." },
      { id: uid("event"), title: "Service model shifts", year: "2028", description: "Support moves toward differentiated pathways.", cause: "Capacity pressure forces clearer choices.", consequence: "Some work is protected, some is stopped.", stakeholders: "Faculties and central teams", signal: "Service catalogues and escalation rules.", plausibility: "Budget and demand make this likely." },
    ];
  });
  s.actions = [
    makeAction("Create a tiered digital teaching support model", "Define core, enhanced and strategic support pathways."),
    makeAction("Invest in AI-enabled assessment design capability", "Build practical support around high-risk assessment redesign."),
    makeAction("Stop bespoke support for low-impact tool requests", "Redirect capacity to reusable patterns and program-level work."),
  ];
  s.actions.forEach((a, i) => {
    s.scenarios.forEach(sc => a.ratings[sc.id] = i === 2 ? "risky" : "useful");
    classifyAction(a);
  });
  s.stressTests = sampleStressTests(s);
  s.weakSignals = sampleWeakSignals(s);
  logDecision(s, "Loaded sample workshop context.");
  return s;
}

function makeCluster(name = "New dynamic condition", forceIds = []) {
  return {
    id: uid("cluster"),
    name,
    description: "",
    forceIds,
    causalNotes: "",
    openQuestions: "",
    extremes: {
      a: { label: "", description: "", visible: "", plausible: "" },
      b: { label: "", description: "", visible: "", plausible: "" },
    },
    impact: 3,
    uncertainty: 3,
    impactWins: 0,
    uncertaintyWins: 0,
  };
}

function makeAction(title = "New strategic action", description = "") {
  return { id: uid("action"), title, description, owner: "", timeframe: "", effort: 2, confidence: 3, nextDecision: "", ratings: {}, classification: "Unclassified" };
}

function makeStressResult(scenarioId, overrides = {}) {
  const result = {
    scenarioId,
    fitScore: 3,
    riskScore: 3,
    workloadBurden: 3,
    confidence: 3,
    strategicValue: 3,
    reversibility: 3,
    resultLabel: "",
    whatHappens: "",
    keyRisks: "",
    adaptationNeeded: "",
    conditionsForSuccess: "",
    earlyWarningSignals: "",
    notes: "",
    ...overrides,
  };
  result.resultLabel = result.resultLabel || stressResultLabel(result);
  return result;
}

function makeStressTest(actionTitle = "New strategy under test", actionDescription = "", scenarios = []) {
  const test = {
    id: uid("stress"),
    actionTitle,
    actionDescription,
    actionType: "Strategy",
    owner: "",
    timeframe: "",
    createdAt: new Date().toISOString(),
    scenarioResults: scenarios.map(sc => makeStressResult(sc.id)),
    overallClassification: "",
    suggestedClassification: "Monitor only",
    overallNotes: "",
    adaptationSummary: "",
    decisionRecommendation: "Hold and monitor",
  };
  updateStressTestClassification(test);
  return test;
}

function makeWeakSignal(title = "New weak signal", scenarioIds = []) {
  const today = new Date().toISOString().slice(0, 10);
  return {
    id: uid("signal"),
    title,
    description: "",
    linkedScenarioIds: scenarioIds,
    category: "Other",
    currentStrength: "Faint",
    confidence: "Medium",
    direction: "Unknown",
    evidence: "",
    source: "",
    owner: "",
    reviewCadence: "Monthly",
    lastReviewed: today,
    nextReview: nextReviewDate(today, "Monthly"),
    notes: "",
    history: [],
  };
}

function sampleStressTests(s) {
  const byName = Object.fromEntries(s.scenarios.map(sc => [sc.name, sc.id]));
  const hub = makeStressTest("Create a central AI teaching support hub", "Coordinate AI teaching support demand, governance, exemplars and triage across the institution.", s.scenarios);
  hub.actionType = "Service change";
  hub.owner = "Central learning support";
  hub.timeframe = "2026-2027";
  const examples = {
    "Coordinated Acceleration": ["Strong fit", 5, 2, 3, 4, 5, 3, "Helps coordinate demand and turn confidence into usable service pathways.", "Scaling too slowly as adoption accelerates.", "Strong governance, faculty pathways and visible service boundaries.", "Clear executive sponsorship and practical faculty engagement.", "Enterprise AI tools enter formal teaching workflows."],
    "Automation Without Absorption": ["Useful but adapt", 4, 4, 5, 3, 5, 3, "The hub becomes essential but risks being overwhelmed by urgent support demand.", "The hub becomes a bottleneck and absorbs every AI anxiety.", "Triage, self-service resources and explicit service boundaries.", "Demand management, reusable patterns and escalation rules.", "Urgent AI-related support requests increase."],
    "Cautious Consolidation": ["Useful but adapt", 3, 3, 3, 3, 4, 4, "The hub is useful if framed as safe guidance rather than aggressive transformation.", "It may be perceived as premature or over-centralised.", "Position as low-risk experimentation, exemplars and policy interpretation.", "Trust-building with governance groups and faculties.", "Governance groups request clearer policy boundaries."],
    "Exhausted Fragmentation": ["Fragile", 2, 4, 4, 2, 3, 3, "Staff may lack capacity to engage unless the hub offers immediate relief.", "Low uptake and reactive escalation.", "Reduce scope and focus on practical relief, triage and templates.", "Low-friction support offers and urgent workload relief.", "Workload comments intensify in staff feedback."],
  };
  hub.scenarioResults = s.scenarios.map(sc => {
    const e = examples[sc.name] || ["Unclear", 3, 3, 3, 3, 3, 3, "", "", "", "", ""];
    return makeStressResult(sc.id, { resultLabel: e[0], fitScore: e[1], riskScore: e[2], workloadBurden: e[3], confidence: e[4], strategicValue: e[5], reversibility: e[6], whatHappens: e[7], keyRisks: e[8], adaptationNeeded: e[9], conditionsForSuccess: e[10], earlyWarningSignals: e[11] });
  });
  updateStressTestClassification(hub);
  const titles = [
    "Shift from bespoke consultation to scalable self-service resources",
    "Establish faculty partnership rhythms for digital teaching support",
    "Build a triage model for learning technology support requests",
    "Develop AI assessment exemplars and reusable patterns",
  ];
  const more = titles.map((title, i) => {
    const test = makeStressTest(title, "Sample strategy prepared for portfolio comparison.", s.scenarios);
    test.actionType = ["Service change", "Initiative", "Policy", "Pilot"][i];
    test.scenarioResults = s.scenarios.map((sc, j) => makeStressResult(sc.id, {
      fitScore: Math.max(2, 5 - ((i + j) % 3)),
      riskScore: 2 + ((i + j) % 3),
      workloadBurden: 2 + ((i + j + 1) % 3),
      confidence: 3 + (j % 2),
      strategicValue: 4,
      reversibility: i === 3 ? 5 : 3,
      whatHappens: "The action creates a clearer service response, but its fit depends on local capacity and confidence.",
      keyRisks: "Uneven uptake, unclear ownership or support demand exceeding capacity.",
      adaptationNeeded: "Scale the scope, clarify service boundaries and watch early demand signals.",
      conditionsForSuccess: "Clear ownership, practical templates and disciplined triage.",
      earlyWarningSignals: sc.fields.signs || "",
    }));
    updateStressTestClassification(test);
    return test;
  });
  return [hub, ...more];
}

function sampleWeakSignals(s) {
  const scenario = name => s.scenarios.find(sc => sc.name === name)?.id;
  const rows = [
    ["Enterprise AI tools are being adopted through formal teaching workflows.", ["Coordinated Acceleration"], "Technology", "Strong", "High", "Increasing"],
    ["Faculties request shared exemplars rather than bespoke advice.", ["Coordinated Acceleration"], "Service demand", "Emerging", "Medium", "Increasing"],
    ["Senior committees ask for evidence of scalable teaching improvement.", ["Coordinated Acceleration"], "Policy / regulation", "Emerging", "High", "Stable"],
    ["Urgent AI-related support requests increase.", ["Automation Without Absorption"], "Service demand", "Strong", "High", "Increasing"],
    ["Staff ask for \"just tell me what to do\" guidance.", ["Automation Without Absorption"], "Staff behaviour", "Emerging", "Medium", "Increasing"],
    ["Support teams report repeated workload spikes.", ["Automation Without Absorption", "Exhausted Fragmentation"], "Workload / capacity", "Critical", "High", "Increasing"],
    ["Local faculty guidance emerges independently.", ["Automation Without Absorption", "Exhausted Fragmentation"], "Sector movement", "Emerging", "Medium", "Increasing"],
    ["Staff prefer low-risk pilots over large-scale change.", ["Cautious Consolidation"], "Staff behaviour", "Emerging", "Medium", "Stable"],
    ["Governance groups request clearer policy boundaries.", ["Cautious Consolidation"], "Policy / regulation", "Strong", "High", "Stable"],
    ["Course teams delay assessment redesign decisions.", ["Cautious Consolidation", "Exhausted Fragmentation"], "Workload / capacity", "Emerging", "Medium", "Increasing"],
    ["Workload comments intensify in staff feedback.", ["Exhausted Fragmentation"], "Stakeholder sentiment", "Critical", "High", "Increasing"],
    ["Teams duplicate guidance because central advice is unclear.", ["Exhausted Fragmentation"], "Service demand", "Strong", "Medium", "Increasing"],
    ["Support requests are increasingly urgent and reactive.", ["Exhausted Fragmentation"], "Service demand", "Strong", "High", "Increasing"],
    ["Staff disengage from optional professional learning.", ["Exhausted Fragmentation"], "Staff behaviour", "Emerging", "Medium", "Increasing"],
  ];
  return rows.map(([title, scenarioNames, category, strength, confidence, direction]) => {
    const signal = makeWeakSignal(title, scenarioNames.map(scenario).filter(Boolean));
    signal.category = category;
    signal.currentStrength = strength;
    signal.confidence = confidence;
    signal.direction = direction;
    signal.description = "Sample weak signal for monitoring scenario activation.";
    signal.evidence = "Sample workshop evidence. Replace with live observations during review.";
    signal.source = "Scenario Studio sample data";
    signal.owner = "Strategy lead";
    signal.history = [{ id: uid("history"), date: signal.lastReviewed, strength, confidence, direction, evidence: signal.evidence, notes: "Initial sample reading." }];
    return signal;
  });
}

function saveState() {
  state.version = STATE_VERSION;
  state.savedAt = new Date().toISOString();
  localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
}

function loadState() {
  for (const key of [STORAGE_KEY, ...LEGACY_STORAGE_KEYS]) {
    try {
      const raw = localStorage.getItem(key);
      if (!raw) continue;
      return migrateState(JSON.parse(raw));
    } catch {
      continue;
    }
  }
  return null;
}

function migrateState(candidate) {
  const base = createEmptyWorkshop();
  const merged = { ...base, ...candidate };
  merged.version = STATE_VERSION;
  merged.ui = { ...base.ui, ...(candidate.ui || {}) };
  merged.ui.guidedMode = candidate.ui?.guidedMode ?? true;
  merged.ui.glossaryOpen = false;
  merged.setup = { ...base.setup, ...(candidate.setup || {}) };
  merged.axes = { ...base.axes, ...(candidate.axes || {}) };
  merged.scenarios = (candidate.scenarios?.length ? candidate.scenarios : base.scenarios).map((sc, i) => ({
    ...base.scenarios[i % 4],
    ...sc,
    fields: { ...(sc.fields || {}) },
    events: sc.events || [],
    critiques: sc.critiques || [],
  }));
  const validRatings = new Set(["strongly useful", "useful", "neutral", "risky", "harmful", "uncertain"]);
  merged.actions = (candidate.actions || []).map(a => {
    const action = { ...makeAction(), ...a, ratings: a.ratings || {} };
    Object.keys(action.ratings).forEach(key => {
      if (!validRatings.has(action.ratings[key])) action.ratings[key] = "uncertain";
    });
    classifyAction(action);
    return action;
  });
  merged.stressTests = (candidate.stressTests || []).map(test => {
    const hydrated = {
      ...makeStressTest(test.actionTitle || "Strategy under test", test.actionDescription || "", stateSafeScenarios(merged)),
      ...test,
      scenarioResults: stateSafeScenarios(merged).map(sc => ({ ...makeStressResult(sc.id), ...(test.scenarioResults || []).find(r => r.scenarioId === sc.id) })),
    };
    hydrated.scenarioResults.forEach(r => { if (!r.resultLabel) r.resultLabel = stressResultLabel(r); });
    updateStressTestClassification(hydrated);
    return hydrated;
  });
  merged.weakSignals = (candidate.weakSignals || []).map(sig => ({ ...makeWeakSignal(sig.title || "Weak signal", sig.linkedScenarioIds || []), ...sig, history: sig.history || [] }));
  merged.signalFilters = { ...base.signalFilters, ...(candidate.signalFilters || {}) };
  merged.parkingLot = (candidate.parkingLot || []).map(p => ({ category: "parking", ...p }));
  merged.implications = { ...base.implications, ...(candidate.implications || {}) };
  merged.minorityReports = candidate.minorityReports || [];
  merged.pairwise = { ...base.pairwise, ...(candidate.pairwise || {}) };
  return merged;
}

function stateSafeScenarios(targetState = state) {
  return targetState.scenarios?.length ? targetState.scenarios : createEmptyWorkshop().scenarios;
}

function setState(mutator, options = {}) {
  if (options.undo !== false) pushUndo();
	  mutator(state);
  syncSelectedAxisEndpoints();
	  saveState();
	  render();
	}

function pushUndo() {
  undoStack.unshift(JSON.stringify(state));
  undoStack = undoStack.slice(0, 25);
}

function undo() {
  const previous = undoStack.shift();
  if (!previous) return saveToast("Nothing to undo.");
  state = migrateState(JSON.parse(previous));
  saveState();
  render();
  saveToast("Undone.");
}

function logDecision(targetState, text) {
  targetState.decisionLog.unshift({ id: uid("decision"), step: targetState.currentStep, text, createdAt: new Date().toISOString() });
}

function escapeHtml(value = "") {
  return String(value).replace(/[&<>"']/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#039;" }[c]));
}

function selectedQuestion() {
  return state.focalQuestions.find(q => q.selected) || state.focalQuestions[0];
}

function forceById(id) {
  return state.drivingForces.find(f => f.id === id);
}

function clusterById(id) {
  return state.clusters.find(c => c.id === id);
}

function activeScenario() {
  if (!activeScenarioId || !state.scenarios.some(s => s.id === activeScenarioId)) activeScenarioId = state.scenarios[0]?.id;
  return state.scenarios.find(s => s.id === activeScenarioId);
}

function scoreQuestion(q) {
  return Object.values(q.scores || {}).reduce((sum, n) => sum + Number(n || 0), 0);
}

function clusterPriority(c) {
  return Number(c.impact || 0) + Number(c.uncertainty || 0) + Number(c.impactWins || 0) + Number(c.uncertaintyWins || 0);
}

function dynamicClusterName(name = "") {
  return /\b(degree|level|pace|extent|capacity|confidence|coherence|pressure|variation|availability|sustainability|intensity|direction)\b/i.test(name);
}

function syncSelectedAxisEndpoints() {
  ["x", "y"].forEach(axisName => {
    const axis = state.axes?.[axisName];
    const cluster = axis?.clusterId ? clusterById(axis.clusterId) : null;
    if (!axis || !cluster || axis.sync === false) return;
    axis.low = cluster.extremes.a.label || axis.low || "";
    axis.high = cluster.extremes.b.label || axis.high || "";
  });
}

function render() {
  const root = $("#app");
  const step = steps[state.currentStep];
  root.innerHTML = `
    <div class="app-shell ${state.ui.roomMode ? "room-mode" : ""}">
      ${renderRail()}
      <main class="main-stage">
        <div class="topbar no-print">
          <div class="progress-wrap"><div class="progress-bar" style="width:${((state.currentStep + 1) / steps.length) * 100}%"></div></div>
          <div class="top-actions">
            <button class="btn small" data-action="undo" ${undoStack.length ? "" : "disabled"}>Undo</button>
            <button class="btn small" data-action="toggleCommands">Commands</button>
            <button class="btn small ${state.ui.guidedMode ? "green" : ""}" data-action="toggleGuided">${state.ui.guidedMode ? "Guided mode" : "Expert mode"}</button>
            <button class="btn small" data-action="toggleGlossary">Glossary</button>
            <button class="btn small ${state.ui.roomMode ? "green" : ""}" data-action="toggleRoom">${state.ui.roomMode ? "Operator mode" : "Room mode"}</button>
            <button class="btn small" data-action="save">Save now</button>
            <button class="btn small" data-action="loadSample">Load sample</button>
            <button class="btn small" data-action="exportJson">Export JSON</button>
          </div>
        </div>
        ${renderOutputStrip()}
        ${renderTransformationMap()}
        <section class="step-header">
          <div class="step-kicker">Step ${state.currentStep} of ${steps.length - 1}</div>
          <h2>${step[0]}</h2>
          <p>${step[1]}</p>
          <div class="output-target">Output target: ${outputTarget(state.currentStep)}</div>
        </section>
        ${state.ui.guidedMode && !state.ui.roomMode ? renderStepGuide() : ""}
        <section class="workspace">${state.ui.roomMode ? renderRoomView() : renderStep()}</section>
        ${state.ui.commandOpen ? renderCommandPalette() : ""}
        ${state.ui.glossaryOpen ? renderGlossaryOverlay() : ""}
        ${renderDecisionGate()}
        <div class="nav-actions no-print" style="justify-content:space-between;margin-top:1rem">
          <button class="btn" data-action="prev" ${state.currentStep === 0 ? "disabled" : ""}>Previous</button>
          <button class="btn primary" data-action="next" ${state.currentStep === steps.length - 1 ? "disabled" : ""}>Next</button>
        </div>
      </main>
      ${renderSideLayer()}
    </div>
  `;
  if (!root.dataset.bound) {
    bindEvents(root);
    root.dataset.bound = "true";
  }
}

function renderCommandPalette() {
  const commands = [
    ["Go to Driving Forces", "commandStep", "2"],
    ["Go to Scenario Matrix", "commandStep", "6"],
    ["Go to Strategic Implications", "commandStep", "10"],
    ["Toggle room mode", "toggleRoom", ""],
    ["Start timer", "timerStart", ""],
    ["Load sample data", "loadSample", ""],
    ["Go to Stress-Test Theatre", "commandStep", "11"],
    ["Go to Weak Signals Monitor", "commandStep", "12"],
    ["Export report", "commandStep", "13"],
  ];
  return `
    <div class="command-backdrop no-print" data-action="toggleCommands">
      <section class="command-palette" onclick="event.stopPropagation()">
        <div class="inline-actions" style="justify-content:space-between">
          <h3>Facilitator Commands</h3>
          <button class="btn small" data-action="toggleCommands">Close</button>
        </div>
        ${commands.map(([label, action, value]) => `<button class="command-row" data-action="${action}" data-value="${value}">${label}<span>${action === "commandStep" ? `Step ${value}` : "Action"}</span></button>`).join("")}
      </section>
    </div>
  `;
}

function renderTransformationMap() {
  if (!state.ui.guidedMode) return "";
  const activeIndex = Math.min(transformation.length - 1, state.currentStep);
  return `
    <section class="transformation-map no-print">
      ${transformation.map((label, i) => `<div class="${i <= activeIndex ? "active" : ""}"><span>${i + 1}</span><strong>${label}</strong></div>`).join("")}
    </section>
  `;
}

function renderStepGuide() {
  const guide = stepGuides[state.currentStep];
  return `
    <section class="guide-panel no-print">
      <div>
        <span class="badge green">In plain English</span>
        <p>${escapeHtml(guide.plain)}</p>
      </div>
      <div>
        <span class="badge blue">Why it matters</span>
        <p>${escapeHtml(guide.why)}</p>
      </div>
      <div>
        <span class="badge gold">Example</span>
        <p>${escapeHtml(guide.example)}</p>
      </div>
      <div>
        <span class="badge rose">Common trap</span>
        <p>${escapeHtml(guide.trap)}</p>
      </div>
      <div class="guide-wide">
        <span class="badge">What good looks like</span>
        <ul>${guide.good.map(item => `<li>${escapeHtml(item)}</li>`).join("")}</ul>
        <p class="reassurance">${escapeHtml(guide.reassurance)}</p>
      </div>
    </section>
  `;
}

function renderGlossaryOverlay() {
  return `
    <div class="command-backdrop no-print" data-action="toggleGlossary">
      <section class="command-palette glossary-panel" onclick="event.stopPropagation()">
        <div class="inline-actions" style="justify-content:space-between">
          <h3>Method Glossary</h3>
          <button class="btn small" data-action="toggleGlossary">Close</button>
        </div>
        <div class="glossary-grid">
          ${glossary.map(([term, definition]) => `<article><h4>${escapeHtml(term)}</h4><p>${escapeHtml(definition)}</p></article>`).join("")}
        </div>
      </section>
    </div>
  `;
}

function renderOutputStrip() {
  const axes = [clusterById(state.axes.x?.clusterId)?.name, clusterById(state.axes.y?.clusterId)?.name].filter(Boolean);
  return `
    <section class="output-strip no-print">
      <div><span>Focal</span><strong>${escapeHtml(selectedQuestion()?.text || state.setup.focalIssue || "Not selected")}</strong></div>
      <div><span>Forces</span><strong>${state.drivingForces.length}</strong></div>
      <div><span>Clusters</span><strong>${state.clusters.length}</strong></div>
      <div><span>Axes</span><strong>${escapeHtml(axes.join(" + ") || "Not selected")}</strong></div>
      <div><span>Robust actions</span><strong>${state.actions.filter(a => a.classification === "Robust action").length}</strong></div>
      <div><span>Stress tests</span><strong>${state.stressTests.length}</strong></div>
      <div><span>Signals</span><strong>${state.weakSignals.length}</strong></div>
      <div><span>Autosave</span><strong>${state.savedAt ? new Date(state.savedAt).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }) : "Ready"}</strong></div>
    </section>
  `;
}

function renderDecisionGate() {
  const checks = [
    ["The room understands the focal issue.", "The opening statement is readable at distance."],
    ["One question is selected.", "The wording includes uncertainty, scope and action relevance."],
    ["Forces are concrete enough to cluster.", "Major categories have been scanned."],
    ["Clusters are named as dynamic conditions.", "Out-of-scope items are parked."],
    ["Each cluster has two structurally different plausible outcomes.", "The extremes are not just good/bad."],
    ["Top-right uncertainties are visible.", "Two axes have been selected or deliberately overridden."],
    ["Axis endpoints are readable.", "Each quadrant describes a distinct future."],
    ["Each scenario has risks, opportunities and early signs.", "The mini matrix still orients the room."],
    ["Events form a causal chain.", "Acceleration, resistance and late signals have been discussed."],
    ["Critiques have been accepted, rejected, parked or edited in.", "Scenarios are distinct and plausible."],
    ["Actions have been tested across all scenarios.", "Start/stop/protect/monitor decisions are captured."],
    ["Important strategies have been stress-tested.", "Adaptations and proceed/hold/stop recommendations are visible."],
    ["Weak signals have owners, evidence and review dates.", "Scenario activation can be explained to colleagues."],
    ["The report has enough detail for people who were not in the room.", "Actions and signals are ready to share."],
  ][state.currentStep];
  return `
    <section class="decision-gate no-print">
      <div><span class="badge green">Decision gate</span><strong>Before moving on, confirm:</strong></div>
      ${checks.map(c => `<label class="check-line"><input type="checkbox"> ${escapeHtml(c)}</label>`).join("")}
    </section>
  `;
}

function outputTarget(step) {
  return [
    "Shared workshop frame and opening statement.",
    "Selected focal question and time horizon.",
    "A bank of categorised driving-force cards.",
    "6 to 10 named clusters of related uncertainty.",
    "Two plausible extremes for each cluster.",
    "Two selected critical uncertainties.",
    "Four named scenario spaces.",
    "Four scenario sketches.",
    "Four causal timelines.",
    "Revised and strengthened scenarios.",
    "Prioritised strategic implications.",
    "Stress-tested strategies with adaptation recommendations.",
    "A living weak-signals monitor linked to scenarios.",
    "A printable report and exportable workshop data.",
  ][step];
}

function renderRail() {
  return `
    <aside class="process-rail no-print">
      <div class="brand">
        <div class="brand-mark">SS</div>
        <h1>Scenario Studio</h1>
        <p>Facilitation console for intuitive logics scenario-thinking workshops.</p>
      </div>
      ${steps.map((s, i) => `
        <button class="rail-step ${i === state.currentStep ? "active" : ""}" data-step="${i}">
          <span class="rail-num">${i}</span>
          <span><span class="rail-label">${s[0]}</span><span class="rail-purpose">${s[1]}</span></span>
        </button>
      `).join("")}
    </aside>
  `;
}

function renderSideLayer() {
  const prompt = prompts[state.currentStep] || [];
  return `
    <aside class="side-layer no-print">
      <details class="side-section" open>
        <summary>Workshop Health</summary>
        <div class="mini-panel">${renderQualityMeter()}</div>
      </details>
      <details class="side-section" open>
        <summary>Facilitator Notes</summary>
        <div class="mini-panel">
          <div class="badge green">Prompt language</div>
          <ul>${prompt.map(p => `<li>${escapeHtml(p)}</li>`).join("")}</ul>
          ${state.ui.guidedMode ? `<div class="method-caption"><strong>Room language:</strong> ${escapeHtml(stepGuides[state.currentStep].plain)}</div>` : ""}
          <div class="inline-actions">
            <button class="btn small" data-action="timerStart">Start 20m</button>
            <button class="btn small" data-action="timerReset">Reset</button>
            <span class="badge blue" id="timer">${formatTime(timerSeconds)}</span>
          </div>
        </div>
      </details>
      <details class="side-section" open>
        <summary>Parking Lot</summary>
        <form class="mini-panel" data-form="parking">
          <select name="category">
            <option value="parking">Parking lot</option>
            <option value="weak-signal">Wildcard / weak signal</option>
            <option value="minority-report">Minority report</option>
          </select>
          <textarea name="text" placeholder="Park a useful out-of-scope idea..."></textarea>
          <button class="btn green small" style="margin-top:.5rem">Park idea</button>
        </form>
        <div>${state.parkingLot.length ? state.parkingLot.map(item => `
          <div class="parking-item">
            <strong>${escapeHtml(item.text)}</strong>
            <div class="inline-actions" style="margin-top:.35rem">
              <span class="badge">${escapeHtml(item.category || "parking")}</span>
              <span class="badge">Step ${item.sourceStep}</span>
              <button class="btn small danger" data-action="deleteParking" data-id="${item.id}">Delete</button>
            </div>
          </div>
        `).join("") : `<div class="empty">No parked ideas yet.</div>`}</div>
      </details>
      <details class="side-section">
        <summary>Decision Log</summary>
        <div>${state.decisionLog.length ? state.decisionLog.map(d => `
          <div class="log-entry"><time>${new Date(d.createdAt).toLocaleString()}</time>${escapeHtml(d.text)}</div>
        `).join("") : `<div class="empty">Key decisions will appear here.</div>`}</div>
      </details>
      <details class="side-section">
        <summary>Minority Reports</summary>
        <form class="mini-panel" data-form="minority">
          <textarea name="text" placeholder="Capture dissent, unresolved tension or an assumption the room did not settle."></textarea>
          <button class="btn green small" style="margin-top:.5rem">Capture</button>
        </form>
        <div>${state.minorityReports.length ? state.minorityReports.map(m => `<div class="log-entry">${escapeHtml(m.text)}<br><span class="badge">Step ${m.sourceStep}</span></div>`).join("") : `<div class="empty">No minority reports yet.</div>`}</div>
      </details>
      <details class="side-section">
        <summary>Quick Glossary</summary>
        <div class="mini-panel">${glossary.slice(0, 5).map(([term, definition]) => `<p><strong>${escapeHtml(term)}:</strong> ${escapeHtml(definition)}</p>`).join("")}<button class="btn small" data-action="toggleGlossary">Open full glossary</button></div>
      </details>
    </aside>
  `;
}

function renderQualityMeter() {
  const checks = [
    Boolean(selectedQuestion()),
    state.drivingForces.length >= 6,
    state.clusters.length >= 2,
    state.clusters.some(c => c.extremes.a.label && c.extremes.b.label),
    Boolean(state.axes.x?.clusterId && state.axes.y?.clusterId),
    state.scenarios.every(s => s.name && s.descriptor),
    state.scenarios.some(s => s.events.length),
    state.actions.length > 0,
    state.stressTests.length > 0,
    state.weakSignals.length > 0,
  ];
  const score = checks.filter(Boolean).length;
  const label = score >= 7 ? "Ready to share" : score >= 4 ? "Developing" : "Early build";
  return `
    <div class="quality-ring" style="--quality:${score / checks.length}">
      <strong>${score}/${checks.length}</strong><span>${label}</span>
    </div>
    <p>${qualityHint()}</p>
  `;
}

function qualityHint() {
  if (!selectedQuestion()) return "Select a focal question to anchor the room.";
  if (state.drivingForces.length < 6) return "Capture more driving forces before clustering.";
  if (state.clusters.length < 2) return "Create at least two dynamic clusters.";
  if (!state.axes.x?.clusterId || !state.axes.y?.clusterId) return "Select two critical uncertainties for the matrix.";
  if (!state.actions.length) return "Add actions so the workshop turns into choices.";
  if (!state.stressTests.length) return "Stress-test one important strategy before sharing.";
  if (!state.weakSignals.length) return "Add weak signals so colleagues can monitor what is emerging.";
  return "The workshop has enough structure for a useful report.";
}

function renderStep() {
  return [
    renderSetup,
    renderFocalQuestion,
    renderDrivingForces,
    renderClustering,
    renderExtremes,
    renderPrioritisation,
    renderScenarioMatrix,
    renderScenarioSketches,
    renderStorylines,
    renderCritique,
    renderStrategicImplications,
    renderStressTestTheatre,
    renderWeakSignalsMonitor,
    renderExport,
  ][state.currentStep]();
}

function renderRoomView() {
  const selected = selectedQuestion();
  if (state.currentStep <= 1) {
    return `
      <section class="room-display">
        <span class="badge green">Participant display</span>
        <h2>${escapeHtml(selected?.text || state.setup.openingStatement || "Focal question emerging")}</h2>
        <p>${escapeHtml(state.setup.desiredOutput || "A shared view of plausible futures and choices now.")}</p>
        ${renderRoomCaption()}
      </section>
    `;
  }
  if (state.currentStep === 2) return `<section class="room-board">${renderRoomCaption()}<h2>Driving Forces</h2><div class="grid three">${state.drivingForces.map(f => forceCard(f, true)).join("")}</div></section>`;
  if (state.currentStep === 3) return `<section class="room-board">${renderRoomCaption()}<h2>Emerging Clusters</h2><div class="cluster-zones">${state.clusters.map(c => `<div class="panel cluster-zone"><h3>${escapeHtml(c.name)}</h3><p>${escapeHtml(c.description || "")}</p><div class="badge">${c.forceIds.length} forces</div></div>`).join("")}</div></section>`;
  if (state.currentStep === 4) return `<section class="room-board">${renderRoomCaption()}<h2>Plausible Extremes</h2><div class="grid two">${state.clusters.map(c => `<div class="panel"><h3>${escapeHtml(c.name)}</h3><div class="split-extremes"><div><strong>${escapeHtml(c.extremes.a.label || "Outcome A")}</strong><p>${escapeHtml(c.extremes.a.description || "")}</p></div><div><strong>${escapeHtml(c.extremes.b.label || "Outcome B")}</strong><p>${escapeHtml(c.extremes.b.description || "")}</p></div></div></div>`).join("")}</div></section>`;
  if (state.currentStep === 5) return `<section class="room-board">${renderRoomCaption()}<h2>Critical Uncertainties</h2><div class="grid two">${[state.axes.x, state.axes.y].map(a => `<div class="display-card"><div class="eyebrow">Selected axis</div><h3>${escapeHtml(clusterById(a?.clusterId)?.name || "Axis not selected")}</h3><p>${escapeHtml(a?.low || "")} &harr; ${escapeHtml(a?.high || "")}</p></div>`).join("")}</div></section>`;
  if (state.currentStep === 6) return `<section class="room-board">${renderRoomCaption()}${renderScenarioMatrix()}</section>`;
  if (state.currentStep <= 9) return `<section class="room-board">${renderRoomCaption()}<h2>Scenario Set</h2><div class="grid four">${state.scenarios.map(s => `<article class="scenario-quadrant"><span class="badge">${escapeHtml(s.icon)}</span><h3>${escapeHtml(s.name)}</h3><p>${escapeHtml(s.descriptor)}</p><p><strong>Early signs:</strong> ${escapeHtml(s.fields.signs || "To be developed")}</p></article>`).join("")}</div></section>`;
  if (state.currentStep === 10) return `<section class="room-board">${renderRoomCaption()}<h2>Strategic Action Portfolio</h2>${renderActionPortfolio()}${renderSignalsDashboard()}</section>`;
  if (state.currentStep === 11) return `<section class="room-board">${renderRoomCaption()}<h2>Strategy Under Test</h2>${renderStressPortfolio()}${renderStressHeatmap()}</section>`;
  if (state.currentStep === 12) return `<section class="room-board">${renderRoomCaption()}<h2>Scenario Weather Map</h2>${renderScenarioWeatherMap()}${renderWeakSignalBoard(true)}</section>`;
  return `<section class="room-board">${renderRoomCaption()}${renderPresentationSummary()}</section>`;
}

function renderRoomCaption() {
  if (!state.ui.guidedMode) return "";
  const guide = stepGuides[state.currentStep];
  return `<div class="room-caption"><strong>What we are doing:</strong> ${escapeHtml(guide.plain)} <span>${escapeHtml(guide.reassurance)}</span></div>`;
}

function renderSetup() {
  const s = state.setup;
  return `
    <div class="grid aside">
      <div class="panel grid two">
        ${input("title", "Workshop title", s.title)}
        ${input("organisation", "Organisation / team", s.organisation)}
        ${input("date", "Date", s.date, "date")}
        ${input("facilitator", "Facilitator", s.facilitator)}
        ${textarea("participants", "Participants", s.participants)}
        ${input("timeHorizon", "Time horizon", s.timeHorizon)}
        ${textarea("focalIssue", "Focal issue", s.focalIssue)}
        ${textarea("desiredOutput", "Desired final output", s.desiredOutput)}
      </div>
      <div class="grid">
        <div class="display-card">
          <div class="eyebrow">Opening display</div>
          <textarea data-setup="openingStatement">${escapeHtml(s.openingStatement)}</textarea>
        </div>
        <div class="panel">
          <h3>Workshop State</h3>
        <div class="inline-actions">
          <button class="btn green" data-action="seedFocal">Create focal question candidate</button>
          <button class="btn" data-action="save">Save now</button>
          <button class="btn" data-action="loadSaved">Load saved workshop</button>
          <button class="btn" data-action="importJson">Import JSON</button>
            <button class="btn danger" data-action="reset">Reset workshop</button>
          </div>
        </div>
      </div>
    </div>
  `;
}

function input(key, labelText, value, type = "text", target = "setup") {
  return `<label>${labelText}<input type="${type}" data-${target}="${key}" value="${escapeHtml(value || "")}"></label>`;
}

function textarea(key, labelText, value, target = "setup") {
  return `<label>${labelText}<textarea data-${target}="${key}">${escapeHtml(value || "")}</textarea></label>`;
}

function renderFocalQuestion() {
  const sorted = [...state.focalQuestions].sort((a, b) => scoreQuestion(b) - scoreQuestion(a));
  return `
    <div class="grid aside">
      <div class="panel">
        <h3>Add candidate focal question</h3>
        <button class="btn green" data-action="seedFocal" style="margin-bottom:.7rem">Use setup focal issue</button>
        <form data-form="focal" class="grid">
          <textarea name="text" placeholder="How might ... evolve by ..., and what would this mean for our choices now?"></textarea>
          <button class="btn green">Add candidate</button>
        </form>
        <div class="mini-panel" style="margin-top:1rem">
          <h3>Refine wording</h3>
          <ul>${prompts[1].map(p => `<li>${p}</li>`).join("")}</ul>
          ${state.ui.guidedMode ? `<div class="example-contrast"><div><strong>Weak</strong><p>What will happen to AI?</p></div><div><strong>Stronger</strong><p>How might AI-enabled teaching support needs evolve by 2029, and what would this mean for service design?</p></div></div>` : ""}
          ${selectedQuestion() ? textarea("text", "Selected wording", selectedQuestion().text, "selected-question") : ""}
        </div>
      </div>
      <div class="grid">
        <div class="grid two">${state.focalQuestions.length ? state.focalQuestions.map(q => focalCard(q)).join("") : `<div class="empty">Add candidate questions or load sample data.</div>`}</div>
        <div class="panel">
          <h3>Ranked candidates</h3>
          ${sorted.length ? sorted.map(q => `
            <div class="ranking-row">
              <div><strong>${escapeHtml(q.text)}</strong><div class="rank-bar"><div class="rank-fill" style="width:${scoreQuestion(q) * 4}%"></div></div></div>
              <span class="badge ${q.selected ? "green" : ""}">${scoreQuestion(q)} / 25</span>
            </div>
          `).join("") : `<div class="empty">Scores will appear here.</div>`}
        </div>
      </div>
    </div>
  `;
}

function focalCard(q) {
  const labels = { relevance: "Strategic relevance", uncertainty: "Genuine uncertainty", scope: "Appropriate scope", actionability: "Actionability", usefulness: "Usefulness" };
  return `
    <article class="card candidate-card ${q.selected ? "selected" : ""}">
      <textarea data-focal-text="${q.id}">${escapeHtml(q.text)}</textarea>
      ${Object.entries(labels).map(([key, label]) => `
        <div class="score-row"><span>${label}</span><input type="range" min="0" max="5" value="${q.scores[key] || 0}" data-focal-score="${q.id}" data-score-key="${key}"><strong>${q.scores[key] || 0}</strong></div>
      `).join("")}
      <div class="inline-actions">
        <span class="badge blue">${scoreQuestion(q)} points</span>
        <button class="btn small green" data-action="selectFocal" data-id="${q.id}">Select</button>
        <button class="btn small danger" data-action="deleteFocal" data-id="${q.id}">Delete</button>
      </div>
    </article>
  `;
}

function renderDrivingForces() {
  const prompt = prompts[2][Math.floor(Date.now() / 3000) % prompts[2].length];
  return `
    <div class="grid aside">
      <div class="panel">
        <h3>Rapid capture</h3>
        <form data-form="force" class="grid">
          <input name="title" placeholder="Example: Staff expect just-in-time support rather than formal training">
          <textarea name="description" placeholder="Description. Enter saves; Shift+Enter adds a line break."></textarea>
          <select name="category">${categories.map(c => `<option>${c}</option>`).join("")}</select>
          <textarea name="notes" placeholder="Notes"></textarea>
          <input name="evidence" placeholder="Evidence or example">
          <button class="btn green">Add force</button>
        </form>
        <div class="mini-panel" style="margin-top:1rem"><span class="badge gold">Brainstorm</span><h3>${prompt}</h3>${state.ui.guidedMode ? `<p><strong>Quick test:</strong> a force should describe something that may change or put pressure on the focal question. “We need a new service” is an action, not a force.</p>` : ""}</div>
      </div>
      <div class="grid three">${state.drivingForces.length ? state.drivingForces.map(forceCard).join("") : `<div class="empty">No driving forces captured yet.</div>`}</div>
    </div>
  `;
}

function forceCard(f, compact = false, contextClusterId = "") {
  const catClass = `category-${(f.category || "Other").split(" ")[0].replace("/", "")}`;
  const cluster = state.clusters.find(c => c.forceIds.includes(f.id));
  return `
    <article class="card force-card ${catClass}" draggable="true" data-force-id="${f.id}">
      <div class="inline-actions" style="justify-content:space-between">
        <span class="badge">${escapeHtml(f.category || "Other")}</span>
        <span class="badge blue">Force ${cluster ? `→ ${escapeHtml(cluster.name)}` : "→ unclustered"}</span>
      </div>
      <h3 contenteditable data-edit-force="${f.id}" data-field="title">${escapeHtml(f.title)}</h3>
      ${compact ? "" : `<p contenteditable data-edit-force="${f.id}" data-field="description">${escapeHtml(f.description || "")}</p>`}
      <div class="inline-actions" style="margin-top:.55rem">
        ${contextClusterId ? `<button class="btn small" data-action="duplicateForce" data-id="${f.id}" data-cluster="${contextClusterId}">Duplicate</button>` : ""}
        <button class="btn small" data-action="parkForce" data-id="${f.id}">Park</button>
        <button class="btn small danger" data-action="deleteForce" data-id="${f.id}">Delete</button>
      </div>
    </article>
  `;
}

function renderClustering() {
  const assigned = new Set(state.clusters.flatMap(c => c.forceIds));
  const unclustered = state.drivingForces.filter(f => !assigned.has(f.id));
  return `
    <div class="cluster-board">
      <div class="panel">
        <div class="inline-actions" style="justify-content:space-between"><h3>Unclustered forces</h3><button class="btn small green" data-action="addCluster">Add cluster</button></div>
        <div class="stack" data-drop-unclustered="true">${unclustered.length ? unclustered.map(f => forceCard(f, true)).join("") : `<div class="empty">All forces are clustered. Drag here to uncluster. Example cluster name: “degree of institutional confidence in AI-enabled teaching”.</div>`}</div>
        <div class="mini-panel" style="margin-top:1rem"><strong>Quality prompt</strong><p>Try to name clusters as dynamic conditions rather than static topics. Example: not “AI”, but “degree of institutional confidence in AI-enabled teaching”.</p>${state.ui.guidedMode ? `<p class="reassurance">If people disagree about a cluster, capture the tension. That disagreement may be a useful uncertainty.</p>` : ""}</div>
      </div>
      <div class="cluster-zones">${state.clusters.length ? state.clusters.map(clusterZone).join("") : `<div class="empty">Create cluster areas, then drag cards into them.</div>`}</div>
    </div>
  `;
}

function clusterZone(c) {
  return `
    <section class="panel cluster-zone" data-cluster-drop="${c.id}">
      <input data-cluster="${c.id}" data-field="name" value="${escapeHtml(c.name)}">
      <textarea data-cluster="${c.id}" data-field="description" placeholder="Cluster description">${escapeHtml(c.description || "")}</textarea>
      <div class="badge ${dynamicClusterName(c.name) ? "green" : "gold"}">${dynamicClusterName(c.name) ? "Dynamic condition" : "Try a dynamic condition name"}</div>
      <div class="drop-list">${c.forceIds.map(id => forceById(id)).filter(Boolean).map(f => forceCard(f, true, c.id)).join("") || `<div class="empty">Drop related forces here.</div>`}</div>
      <textarea data-cluster="${c.id}" data-field="causalNotes" placeholder="Causal logic notes">${escapeHtml(c.causalNotes || "")}</textarea>
      <textarea data-cluster="${c.id}" data-field="openQuestions" placeholder="Open questions">${escapeHtml(c.openQuestions || "")}</textarea>
      <div class="inline-actions"><button class="btn small danger" data-action="deleteCluster" data-id="${c.id}">Delete cluster</button></div>
    </section>
  `;
}

function renderExtremes() {
  return `
    <div class="grid">
      ${state.ui.guidedMode ? `<section class="panel example-contrast"><div><strong>Weak pair</strong><p>Good AI adoption vs bad AI adoption.</p></div><div><strong>Stronger pair</strong><p>Coordinated adoption with trusted guardrails vs fragmented caution and local workarounds.</p></div></section>` : ""}
      ${state.clusters.length ? state.clusters.map(c => `
        <section class="panel">
          <div class="inline-actions" style="justify-content:space-between"><h3>${escapeHtml(c.name)}</h3>${extremeWarning(c)}</div>
          <div class="split-extremes">
            ${extremeEditor(c, "a", "Outcome A")}
            ${extremeEditor(c, "b", "Outcome B")}
          </div>
        </section>
      `).join("") : `<div class="empty">Create clusters first.</div>`}
    </div>
  `;
}

function extremeWarning(c) {
  const weak = ["a", "b"].some(k => (c.extremes[k].label || "").length < 5 || (c.extremes[k].description || "").length < 20);
  return weak ? `<span class="badge rose">Needs stronger plausible extremes</span>` : `<span class="badge green">Plausible pair captured</span>`;
}

function extremeEditor(c, key, title) {
  const e = c.extremes[key];
  return `
    <div class="extreme-side">
      <h3>${title}</h3>
      ${["label", "description", "visible", "plausible"].map(field => `
        <label>${field === "visible" ? "What would be visible" : field === "plausible" ? "Why this is plausible" : field}
          <textarea data-extreme="${c.id}" data-side="${key}" data-field="${field}">${escapeHtml(e[field] || "")}</textarea>
        </label>
      `).join("")}
    </div>
  `;
}

function renderPrioritisation() {
  const ranked = [...state.clusters].sort((a, b) => clusterPriority(b) - clusterPriority(a));
  return `
    <div class="grid">
      <div class="grid two">
      <section class="panel">
        <h3>Mode A: Impact / uncertainty matrix</h3>
        ${state.ui.guidedMode ? `<div class="method-caption"><strong>How to read this:</strong> impact means “would it matter?” uncertainty means “could it plausibly go different ways?” The top-right quadrant is useful because it is both consequential and unresolved.</div>` : ""}
          <div class="matrix-wrap">
            <div class="axis-y">Higher impact</div>
            <div class="impact-matrix">
              ${["Low uncertainty / high impact", "Critical uncertainties", "Low priority", "High uncertainty / lower impact"].map((label, i) => `
                <div class="quadrant ${i === 1 ? "critical" : ""}" data-matrix-quadrant="${i}">
                  <strong>${label}</strong>
                  ${state.clusters.filter(c => quadrantFor(c) === i).map(c => clusterPriorityCard(c)).join("")}
                </div>
              `).join("")}
            </div>
            <div></div><div class="axis-x">Higher uncertainty</div>
          </div>
        </section>
        <section class="panel">
          <h3>Mode B: Pairwise comparison</h3>
          ${renderPairwise("impact")}
          ${renderPairwise("uncertainty")}
          <h3>Priority ranking</h3>
          ${ranked.map(c => `
            <div class="ranking-row">
              <div><strong>${escapeHtml(c.name)}</strong><div class="rank-bar"><div class="rank-fill" style="width:${Math.min(100, clusterPriority(c) * 8)}%"></div></div></div>
              <span class="badge">${clusterPriority(c)}</span>
            </div>
          `).join("")}
          <div class="inline-actions">
            <button class="btn green" data-action="recommendAxes">Use recommended axes</button>
          </div>
        </section>
      </div>
      <section class="panel">
        <h3>Selected critical uncertainties</h3>
        <div class="grid two">
          ${axisPicker("x", "Horizontal axis")}
          ${axisPicker("y", "Vertical axis")}
        </div>
      </section>
    </div>
  `;
}

function quadrantFor(c) {
  const highI = Number(c.impact) >= 4;
  const highU = Number(c.uncertainty) >= 4;
  if (highI && !highU) return 0;
  if (highI && highU) return 1;
  if (!highI && !highU) return 2;
  return 3;
}

function clusterPriorityCard(c) {
  return `
    <article class="card" draggable="true" data-cluster-card="${c.id}">
      <strong>${escapeHtml(c.name)}</strong>
      <div class="score-row"><span>Impact</span><input type="range" min="1" max="5" value="${c.impact}" data-cluster-score="${c.id}" data-score-key="impact"><strong>${c.impact}</strong></div>
      <div class="score-row"><span>Uncertainty</span><input type="range" min="1" max="5" value="${c.uncertainty}" data-cluster-score="${c.id}" data-score-key="uncertainty"><strong>${c.uncertainty}</strong></div>
    </article>
  `;
}

function renderPairwise(kind) {
  const pairs = makePairs(state.clusters);
  const completed = new Set(state.pairwise[kind] || []);
  const remainingPairs = pairs.filter(pair => !completed.has(pairKey(pair)));
  const cursorKey = kind === "impact" ? "cursorImpact" : "cursorUncertainty";
  const cursor = state.pairwise[cursorKey] || 0;
  if (!pairs.length) return `<div class="empty">Create at least two clusters for pairwise comparison.</div>`;
  if (!remainingPairs.length) return `
    <div class="mini-panel">
      <div class="badge green">${kind} complete</div>
      <h3>All pairwise ${kind} comparisons have been completed.</h3>
      <button class="btn small" data-action="resetPairwise" data-kind="${kind}">Reset ${kind}</button>
    </div>
  `;
  const pair = remainingPairs[cursor % remainingPairs.length];
  return `
    <div class="mini-panel">
      <div class="badge ${kind === "impact" ? "blue" : "gold"}">${kind}</div>
      <p>${pairs.length - remainingPairs.length} of ${pairs.length} comparisons complete</p>
      <h3>${kind === "impact" ? "Which has greater impact on the focal question?" : "Which is more uncertain over the time horizon?"}</h3>
      <div class="grid two">
        ${pair.map(id => `<button class="card pairwise-card" data-action="pairwiseWin" data-kind="${kind}" data-id="${id}"><strong>${escapeHtml(clusterById(id)?.name || "")}</strong></button>`).join("")}
      </div>
    </div>
  `;
}

function makePairs(items) {
  const pairs = [];
  for (let i = 0; i < items.length; i++) for (let j = i + 1; j < items.length; j++) pairs.push([items[i].id, items[j].id]);
  return pairs;
}

function pairKey(pair) {
  return [...pair].sort().join("|");
}

function axisPicker(axis, label) {
  const value = state.axes[axis]?.clusterId || "";
  return `
    <label>${label}
      <select data-axis="${axis}">
        <option value="">Choose uncertainty</option>
        ${state.clusters.map(c => `<option value="${c.id}" ${value === c.id ? "selected" : ""}>${escapeHtml(c.name)}</option>`).join("")}
      </select>
    </label>
  `;
}

function renderScenarioMatrix() {
  const x = hydrateAxis(state.axes.x);
  const y = hydrateAxis(state.axes.y);
  return `
    <div class="grid">
      <section class="panel">
        <div class="inline-actions">
          <button class="btn" data-action="swapAxes">Swap axes</button>
          <button class="btn" data-action="reverseX">Reverse horizontal</button>
          <button class="btn" data-action="reverseY">Reverse vertical</button>
          <span class="badge green">Quality: four genuinely different futures</span>
        </div>
        ${state.ui.guidedMode ? `<div class="method-caption"><strong>How to read the matrix:</strong> each quadrant combines one endpoint from each axis. The group is not voting for the best future; it is exploring four different operating environments.</div>` : ""}
      </section>
      <div class="matrix-wrap">
        <div class="axis-y"><span>${escapeHtml(y.high || "High vertical")}</span><span>${escapeHtml(y.low || "Low vertical")}</span></div>
        <div class="scenario-matrix">
          ${state.scenarios.map((sc, i) => scenarioQuadrant(sc, i, x, y)).join("")}
        </div>
        <div></div><div class="axis-x"><span>${escapeHtml(x.low || "Low horizontal")}</span><strong>${escapeHtml(clusterById(x.clusterId)?.name || "Horizontal uncertainty")}</strong><span>${escapeHtml(x.high || "High horizontal")}</span></div>
      </div>
      <section class="panel grid two">
        ${axisEndpointEditor("x", x, "Horizontal")}
        ${axisEndpointEditor("y", y, "Vertical")}
      </section>
    </div>
  `;
}

function hydrateAxis(axis) {
  if (!axis) return { low: "", high: "", clusterId: "" };
  const c = clusterById(axis.clusterId);
  return {
    ...axis,
    low: axis.low || c?.extremes?.a?.label || "",
    high: axis.high || c?.extremes?.b?.label || "",
  };
}

function axisEndpointEditor(axis, hydrated, label) {
  return `
    <div class="mini-panel">
      <h3>${label} endpoint labels</h3>
      <label>Low / left / bottom<input data-axis-endpoint="${axis}" data-field="low" value="${escapeHtml(hydrated.low || "")}"></label>
      <label>High / right / top<input data-axis-endpoint="${axis}" data-field="high" value="${escapeHtml(hydrated.high || "")}"></label>
    </div>
  `;
}

function scenarioQuadrant(sc, i, x = hydrateAxis(state.axes.x), y = hydrateAxis(state.axes.y)) {
  const combos = [
    [x.low, y.high],
    [x.high, y.high],
    [x.low, y.low],
    [x.high, y.low],
  ][i] || ["", ""];
  return `
    <article class="scenario-quadrant">
      <span class="badge">${escapeHtml(sc.icon || "Scenario")}</span>
      <span class="badge axis-combo">${escapeHtml(combos[0] || "X endpoint")} / ${escapeHtml(combos[1] || "Y endpoint")}</span>
      <textarea class="scenario-name" data-scenario="${sc.id}" data-field="name" placeholder="Scenario name">${escapeHtml(sc.name)}</textarea>
      <textarea data-scenario="${sc.id}" data-field="descriptor" placeholder="One-sentence descriptor">${escapeHtml(sc.descriptor || "")}</textarea>
      <div class="signal-ticker">Early signal: ${escapeHtml(sc.fields.signs || "to be defined")}</div>
    </article>
  `;
}

function renderScenarioSketches() {
  const sc = activeScenario();
  if (!sc) return `<div class="empty">No scenarios available.</div>`;
  const fields = [
    ["feel", "What the world feels like"],
    ["changed", "What has changed"],
    ["same", "What has stayed the same"],
    ["benefits", "Who benefits"],
    ["struggles", "Who struggles"],
    ["easier", "What becomes easier"],
    ["harder", "What becomes harder"],
    ["risks", "Risks"],
    ["opportunities", "Opportunities"],
    ["signs", "Early signs"],
  ];
  return `
    <div class="tabs">${state.scenarios.map(s => `<button class="tab ${s.id === sc.id ? "active" : ""}" data-action="activeScenario" data-id="${s.id}">${escapeHtml(s.name)}</button>`).join("")}</div>
    <div class="grid aside">
      <section class="panel scenario-card active">
        <div class="inline-actions" style="justify-content:space-between">
          <h3>${escapeHtml(sc.name)}</h3>
          ${miniMatrix(sc.quadrant)}
        </div>
        <label>One-sentence description<textarea data-scenario="${sc.id}" data-field="descriptor">${escapeHtml(sc.descriptor || "")}</textarea></label>
        <div class="grid two">${fields.map(([key, label]) => `<label>${label}<textarea data-scenario-field="${sc.id}" data-field="${key}">${escapeHtml(sc.fields[key] || "")}</textarea></label>`).join("")}</div>
      </section>
      <section class="panel">
        <h3>Scenario texture</h3>
        <p>Use this view to make each quadrant vivid enough that the group can reason inside it rather than merely label it.</p>
        <div class="display-card" style="min-height:280px"><div class="eyebrow">${escapeHtml(sc.name)}</div><div style="font-size:2rem;line-height:1.15">${escapeHtml(sc.descriptor || "A scenario space waiting to be made concrete.")}</div></div>
      </section>
    </div>
  `;
}

function miniMatrix(active) {
  return `<div class="mini-matrix">${[0,1,2,3].map(i => `<div class="mini-cell ${i === active ? "active" : ""}"></div>`).join("")}</div>`;
}

function renderStorylines() {
  const sc = activeScenario();
  if (!sc) return `<div class="empty">No scenarios available.</div>`;
  return `
    <div class="tabs">${state.scenarios.map(s => `<button class="tab ${s.id === sc.id ? "active" : ""}" data-action="activeScenario" data-id="${s.id}">${escapeHtml(s.name)}</button>`).join("")}</div>
    <div class="panel">
      <div class="inline-actions" style="justify-content:space-between"><h3>${escapeHtml(sc.name)} timeline</h3><button class="btn green" data-action="addEvent" data-id="${sc.id}">Add event</button></div>
      <div class="timeline">${sc.events.length ? sc.events.map(eventCard).join("") : `<div class="empty">Add events to build the causal storyline.</div>`}</div>
      ${state.ui.guidedMode ? `<div class="method-caption"><strong>Causal chain starter:</strong> Because one thing changed, another thing became more likely, which then changed what staff, students or leaders did.</div>` : ""}
    </div>
  `;
}

function eventCard(e) {
  return `
    <article class="card event-card" draggable="true" data-event-id="${e.id}">
      <input data-event="${e.id}" data-field="year" value="${escapeHtml(e.year || "")}" placeholder="Year or phase">
      ${["title", "description", "cause", "consequence", "stakeholders", "signal", "plausibility"].map(field => `<label>${field}<textarea data-event="${e.id}" data-field="${field}">${escapeHtml(e[field] || "")}</textarea></label>`).join("")}
      <button class="btn small danger" data-action="deleteEvent" data-id="${e.id}">Delete</button>
    </article>
  `;
}

function renderCritique() {
  const sc = activeScenario();
  if (!sc) return `<div class="empty">No scenarios available.</div>`;
  const critiquePrompts = prompts[9].concat(["What assumption does this rely on?", "What are we avoiding?", "What would surprise us?"]);
  return `
    <div class="tabs">${state.scenarios.map(s => `<button class="tab ${s.id === sc.id ? "active" : ""}" data-action="activeScenario" data-id="${s.id}">${escapeHtml(s.name)}</button>`).join("")}</div>
    <div class="grid aside">
      <section class="panel">
        <h3>Current scenario summary</h3>
        <p><strong>${escapeHtml(sc.name)}</strong></p>
        <p>${escapeHtml(sc.descriptor || "")}</p>
        <div class="grid two">
          <div class="mini-panel"><strong>Risks</strong><p>${escapeHtml(sc.fields.risks || "Missing")}</p></div>
          <div class="mini-panel"><strong>Early signs</strong><p>${escapeHtml(sc.fields.signs || "Missing")}</p></div>
        </div>
      </section>
      <section class="panel">
        <h3>Critique notes</h3>
        ${state.ui.guidedMode ? `<div class="method-caption"><strong>Reframe critique:</strong> this is not negativity. It is a stress test that makes scenarios harder to dismiss.</div>` : ""}
        <form data-form="critique" data-id="${sc.id}" class="grid">
          <select name="prompt">${critiquePrompts.map(p => `<option>${escapeHtml(p)}</option>`).join("")}</select>
          <textarea name="text" placeholder="Capture critique or revision action"></textarea>
          <button class="btn green">Add critique</button>
        </form>
        <div class="grid two" style="margin-top:1rem">${sc.critiques.length ? sc.critiques.map(n => critiqueCard(sc.id, n)).join("") : `<div class="empty">Challenge notes will appear here.</div>`}</div>
      </section>
    </div>
  `;
}

function critiqueCard(scenarioId, n) {
  return `
    <article class="card">
      <p contenteditable data-critique="${scenarioId}" data-id="${n.id}">${escapeHtml(n.text)}</p>
      <select data-critique-status="${scenarioId}" data-id="${n.id}">
        ${["accepted", "edited", "parked", "rejected"].map(v => `<option ${n.status === v ? "selected" : ""}>${v}</option>`).join("")}
      </select>
      <button class="btn small danger" data-action="deleteCritique" data-scenario="${scenarioId}" data-id="${n.id}">Delete</button>
    </article>
  `;
}

function renderStrategicImplications() {
  return `
    <div class="grid">
      <section class="panel">
        <form data-form="action" class="grid two">
          <input name="title" placeholder="Strategic action title">
          <input name="owner" placeholder="Owner optional">
          <textarea name="description" placeholder="Action description"></textarea>
          <input name="timeframe" placeholder="Timeframe optional">
          <input name="nextDecision" placeholder="Next decision or follow-up">
          <label>Effort level<input type="range" name="effort" min="1" max="5" value="2"></label>
          <label>Confidence level<input type="range" name="confidence" min="1" max="5" value="3"></label>
          <button class="btn green">Add action</button>
        </form>
      </section>
      <section class="panel">
        <h3>Scenario testing matrix</h3>
        ${state.ui.guidedMode ? `<div class="example-contrast"><div><strong>Robust</strong><p>Useful in most futures, even if the world changes.</p></div><div><strong>Contingent</strong><p>Useful only if certain signals appear.</p></div><div><strong>Hedging</strong><p>Low-cost option that keeps choices open.</p></div></div>` : ""}
        ${state.actions.length ? actionMatrix() : `<div class="empty">Add actions to test them across the four scenarios.</div>`}
      </section>
      <section class="grid five">${["Robust action", "Contingent action", "Hedging action", "Fragile action", "Stop / avoid"].map(cls => `
        <div class="mini-panel"><h3>${cls}</h3>${state.actions.filter(a => a.classification === cls).map(a => `<p>${escapeHtml(a.title)}</p>`).join("") || "<p>No actions yet.</p>"}</div>
      `).join("")}</section>
      <section class="panel grid three">
        ${["start", "stop", "protect", "monitor", "decideNow", "defer"].map(key => textarea(key, labelFromKey(key), state.implications?.[key] || "", "implication")).join("")}
      </section>
    </div>
  `;
}

function labelFromKey(key) {
  return ({ start: "What should we start?", stop: "What should we stop?", protect: "What should we protect?", monitor: "What should we monitor?", decideNow: "What decision should be made now?", defer: "What decision should be deferred?" })[key];
}

function actionMatrix() {
  const choices = ["strongly useful", "useful", "neutral", "risky", "harmful", "uncertain"];
  return `
    <table class="testing-table">
      <thead><tr><th>Action</th>${state.scenarios.map(s => `<th>${escapeHtml(s.name)}</th>`).join("")}<th>Classification</th><th></th></tr></thead>
      <tbody>${state.actions.map(a => `
        <tr>
          <td>
            <input data-action-edit="${a.id}" data-field="title" value="${escapeHtml(a.title)}">
            <textarea data-action-edit="${a.id}" data-field="description">${escapeHtml(a.description)}</textarea>
            <div class="grid two">
              <input data-action-edit="${a.id}" data-field="owner" value="${escapeHtml(a.owner || "")}" placeholder="Owner">
              <input data-action-edit="${a.id}" data-field="timeframe" value="${escapeHtml(a.timeframe || "")}" placeholder="Timeframe">
            </div>
            <label>Effort <input type="range" min="1" max="5" value="${a.effort}" data-action-range="${a.id}" data-field="effort"></label>
            <label>Confidence <input type="range" min="1" max="5" value="${a.confidence}" data-action-range="${a.id}" data-field="confidence"></label>
            <input data-action-edit="${a.id}" data-field="nextDecision" value="${escapeHtml(a.nextDecision || "")}" placeholder="Next decision">
          </td>
          ${state.scenarios.map(s => `<td><select data-action-rating="${a.id}" data-scenario="${s.id}">${choices.map(c => `<option ${a.ratings[s.id] === c ? "selected" : ""}>${c}</option>`).join("")}</select></td>`).join("")}
          <td><span class="badge ${classBadge(a.classification)}">${escapeHtml(a.classification)}</span></td>
          <td><button class="btn small danger" data-action="deleteAction" data-id="${a.id}">Delete</button></td>
        </tr>
      `).join("")}</tbody>
    </table>
  `;
}

function classBadge(cls) {
  if (cls.includes("Robust")) return "green";
  if (cls.includes("Contingent")) return "blue";
  if (cls.includes("Hedging")) return "gold";
  if (cls.includes("Fragile")) return "rose";
  if (cls.includes("Stop")) return "rose";
  return "";
}

function activeStressTest() {
  if (!state.ui.activeStressId || !state.stressTests.some(t => t.id === state.ui.activeStressId)) state.ui.activeStressId = state.stressTests[0]?.id;
  return state.stressTests.find(t => t.id === state.ui.activeStressId);
}

function renderStressTestTheatre() {
  const test = activeStressTest();
  return `
    <div class="grid">
      <section class="theatre-hero">
        <div>
          <span class="badge green">Scenario Stress-Test Theatre</span>
          <h3>Put one strategy under the lights.</h3>
          <p>Ask how this action behaves in each future, what would need to change, and whether the recommendation should be proceed, pilot, hold or stop.</p>
        </div>
        <form data-form="stress" class="stress-create">
          <select name="sourceAction">
            <option value="">Start from blank strategy</option>
            ${state.actions.map(a => `<option value="${a.id}">${escapeHtml(a.title)}</option>`).join("")}
          </select>
          <input name="title" placeholder="Strategy, initiative or decision to test">
          <button class="btn green">Add stress test</button>
        </form>
      </section>
      ${state.stressTests.length ? `
        <div class="tabs">${state.stressTests.map(t => `<button class="tab ${t.id === test?.id ? "active" : ""}" data-action="activeStress" data-id="${t.id}">${escapeHtml(t.actionTitle)}</button>`).join("")}</div>
        ${test ? renderStressTestEditor(test) : ""}
        <section class="grid two">
          ${renderStressPortfolio()}
          ${renderStressHeatmap()}
        </section>
      ` : `<div class="empty">Add a strategy to test, or load sample data to demonstrate the theatre immediately.</div>`}
    </div>
  `;
}

function renderStressTestEditor(test) {
  updateStressTestClassification(test);
  return `
    <section class="stress-stage">
      <aside class="strategy-card">
        <span class="badge ${classificationBadge(test.overallClassification)}">${escapeHtml(test.overallClassification || "Unclassified")}</span>
        <label>Action title<textarea data-stress="${test.id}" data-field="actionTitle">${escapeHtml(test.actionTitle)}</textarea></label>
        <label>Description<textarea data-stress="${test.id}" data-field="actionDescription">${escapeHtml(test.actionDescription || "")}</textarea></label>
        <div class="grid two">
          <label>Type<select data-stress-select="${test.id}" data-field="actionType">${stressActionTypes.map(v => `<option ${test.actionType === v ? "selected" : ""}>${v}</option>`).join("")}</select></label>
          <label>Timeframe<input data-stress="${test.id}" data-field="timeframe" value="${escapeHtml(test.timeframe || "")}"></label>
          <label>Owner<input data-stress="${test.id}" data-field="owner" value="${escapeHtml(test.owner || "")}"></label>
          <label>Recommendation<select data-stress-select="${test.id}" data-field="decisionRecommendation">${stressRecommendations.map(v => `<option ${test.decisionRecommendation === v ? "selected" : ""}>${v}</option>`).join("")}</select></label>
        </div>
        <div class="suggestion-box">
          <span class="badge blue">Transparent scoring</span>
          <p>Suggested: <strong>${escapeHtml(test.suggestedClassification || "Monitor only")}</strong>. The facilitator can override this when the room has a better judgement.</p>
        </div>
        <label>Overall classification<select data-stress-select="${test.id}" data-field="overallClassification">${stressClassifications.map(v => `<option ${test.overallClassification === v ? "selected" : ""}>${v}</option>`).join("")}</select></label>
        <label>Adaptation summary<textarea data-stress="${test.id}" data-field="adaptationSummary">${escapeHtml(test.adaptationSummary || "")}</textarea></label>
        <label>Overall notes<textarea data-stress="${test.id}" data-field="overallNotes">${escapeHtml(test.overallNotes || "")}</textarea></label>
        <div class="inline-actions">
          <button class="btn small" data-action="duplicateStress" data-id="${test.id}">Duplicate</button>
          <button class="btn small danger" data-action="deleteStress" data-id="${test.id}">Delete</button>
        </div>
      </aside>
      <div class="scenario-stress-grid">
        ${state.scenarios.map(sc => renderStressScenarioPanel(test, test.scenarioResults.find(r => r.scenarioId === sc.id) || makeStressResult(sc.id), sc)).join("")}
      </div>
    </section>
  `;
}

function renderStressScenarioPanel(test, result, scenario) {
  const viability = stressViability(result);
  return `
    <article class="stress-scenario-card">
      <div class="inline-actions" style="justify-content:space-between">
        <div>
          <span class="badge">${escapeHtml(scenario.icon || "Scenario")}</span>
          <h3>${escapeHtml(scenario.name)}</h3>
        </div>
        <span class="stress-score">${viability}</span>
      </div>
      <select data-stress-result-select="${test.id}" data-result="${result.scenarioId}" data-field="resultLabel">
        ${stressLabels.map(v => `<option ${result.resultLabel === v ? "selected" : ""}>${v}</option>`).join("")}
      </select>
      ${[
        ["fitScore", "Fit"],
        ["riskScore", "Risk"],
        ["workloadBurden", "Workload"],
        ["confidence", "Confidence"],
        ["strategicValue", "Strategic value"],
        ["reversibility", "Reversibility"],
      ].map(([field, label]) => `
        <div class="score-row compact">
          <span>${label}</span>
          <input type="range" min="1" max="5" value="${Number(result[field] || 3)}" data-stress-range="${test.id}" data-result="${result.scenarioId}" data-field="${field}">
          <strong>${Number(result[field] || 3)}</strong>
        </div>
      `).join("")}
      ${[
        ["whatHappens", "What happens in this scenario"],
        ["keyRisks", "Key risks"],
        ["adaptationNeeded", "Adaptation needed"],
        ["conditionsForSuccess", "Conditions for success"],
        ["earlyWarningSignals", "Early warning signals"],
        ["notes", "Notes"],
      ].map(([field, label]) => `<label>${label}<textarea data-stress-result="${test.id}" data-result="${result.scenarioId}" data-field="${field}">${escapeHtml(result[field] || "")}</textarea></label>`).join("")}
    </article>
  `;
}

function classificationBadge(classification = "") {
  if (classification.includes("Robust") || classification.includes("Worth")) return "green";
  if (classification.includes("Contingent") || classification.includes("Monitor")) return "blue";
  if (classification.includes("risk")) return "gold";
  if (classification.includes("Fragile") || classification.includes("Stop")) return "rose";
  return "";
}

function renderStressPortfolio() {
  const tests = state.stressTests || [];
  return `
    <section class="panel">
      <div class="inline-actions" style="justify-content:space-between"><h3>Strategy Portfolio</h3><span class="badge">${tests.length} tests</span></div>
      <div class="stress-portfolio">
        ${stressClassifications.map(cls => `
          <div class="portfolio-lane">
            <strong>${escapeHtml(cls)}</strong>
            ${tests.filter(t => t.overallClassification === cls).map(t => `<button class="portfolio-token ${classificationBadge(cls)}" data-action="activeStress" data-id="${t.id}">${escapeHtml(t.actionTitle)}</button>`).join("") || `<span class="empty-token">None</span>`}
          </div>
        `).join("")}
      </div>
    </section>
  `;
}

function renderStressHeatmap() {
  const tests = state.stressTests || [];
  return `
    <section class="panel">
      <div class="inline-actions" style="justify-content:space-between"><h3>Scenario Fit Heatmap</h3><span class="badge gold">Fit minus risk/workload</span></div>
      ${tests.length ? `<table class="heatmap-table">
        <thead><tr><th>Strategy</th>${state.scenarios.map(sc => `<th>${escapeHtml(sc.name)}</th>`).join("")}</tr></thead>
        <tbody>${tests.map(t => `<tr><td>${escapeHtml(t.actionTitle)}</td>${state.scenarios.map(sc => {
          const result = t.scenarioResults.find(r => r.scenarioId === sc.id) || makeStressResult(sc.id);
          const score = stressViability(result);
          return `<td><button class="heat-cell ${score >= 4 ? "good" : score >= 2 ? "watch" : "risk"}" data-action="activeStress" data-id="${t.id}">${score}<span>${escapeHtml(result.resultLabel)}</span></button></td>`;
        }).join("")}</tr>`).join("")}</tbody>
      </table>` : `<div class="empty">No strategies tested yet.</div>`}
    </section>
  `;
}

function activeWeakSignal() {
  if (!state.ui.activeSignalId || !state.weakSignals.some(sig => sig.id === state.ui.activeSignalId)) state.ui.activeSignalId = state.weakSignals[0]?.id;
  return state.weakSignals.find(sig => sig.id === state.ui.activeSignalId);
}

function renderWeakSignalsMonitor() {
  return `
    <div class="grid">
      <section class="signal-hero">
        <div>
          <span class="badge green">Weak Signals Monitor</span>
          <h3>Turn scenarios into a living sensing system.</h3>
          <p>Track faint evidence, review it on a cadence, and show which scenarios may be becoming more active.</p>
        </div>
        <div class="inline-actions">
          <button class="btn green" data-action="importScenarioSignals">Import early signs from scenarios</button>
          <button class="btn" data-action="addSignal">Add blank signal</button>
        </div>
      </section>
      ${renderScenarioWeatherMap()}
      <section class="grid aside">
        <div>
          ${renderSignalFilters()}
          ${renderWeakSignalBoard(false)}
        </div>
        ${renderWeakSignalDetail(activeWeakSignal())}
      </section>
    </div>
  `;
}

function renderScenarioWeatherMap() {
  return `
    <section class="panel">
      <div class="inline-actions" style="justify-content:space-between"><h3>Scenario Weather Map</h3><span class="badge blue">Activation = signal strength x confidence x direction</span></div>
      <div class="weather-grid">
        ${state.scenarios.map(sc => {
          const activation = scenarioActivation(sc.id);
          return `<article class="weather-card ${activation.label.toLowerCase().replaceAll(" ", "-")}">
            <div class="weather-ring" style="--activation:${activation.activationScore / 100}"><strong>${activation.activationScore}%</strong><span>${escapeHtml(activation.label)}</span></div>
            <h3>${escapeHtml(sc.name)}</h3>
            <p>${activation.signalCount} linked signals. ${escapeHtml(activation.confidenceSummary)}.</p>
            <div>${activation.topSignals.map(sig => `<span class="signal-chip">${escapeHtml(sig.title)}</span>`).join("") || `<span class="signal-chip">No linked signals yet</span>`}</div>
          </article>`;
        }).join("")}
      </div>
    </section>
  `;
}

function renderSignalFilters() {
  const f = state.signalFilters || {};
  return `
    <section class="panel no-print">
      <div class="inline-actions signal-filters">
        ${filterSelect("scenario", ["All", ...state.scenarios.map(sc => sc.id)], v => v === "All" ? "All scenarios" : state.scenarios.find(sc => sc.id === v)?.name || v)}
        ${filterSelect("category", ["All", ...signalCategories])}
        ${filterSelect("strength", ["All", ...signalStrengths])}
        ${filterSelect("confidence", ["All", ...signalConfidences])}
        ${filterSelect("direction", ["All", ...signalDirections])}
        <label class="check-line compact"><input type="checkbox" data-signal-filter="reviewDue" ${f.reviewDue ? "checked" : ""}> Review due</label>
        <select data-signal-filter="sort">
          ${[["strongest", "Strongest first"], ["due", "Review due first"], ["newest", "Newest review"]].map(([value, label]) => `<option value="${value}" ${f.sort === value ? "selected" : ""}>${label}</option>`).join("")}
        </select>
      </div>
    </section>
  `;
}

function filterSelect(key, values, labeler = v => v) {
  const current = state.signalFilters?.[key] || "All";
  return `<select data-signal-filter="${key}">${values.map(v => `<option value="${escapeHtml(v)}" ${current === v ? "selected" : ""}>${escapeHtml(labeler(v))}</option>`).join("")}</select>`;
}

function filteredWeakSignals() {
  const f = state.signalFilters || {};
  const today = new Date().toISOString().slice(0, 10);
  let signals = [...(state.weakSignals || [])].filter(sig => {
    if (f.scenario && f.scenario !== "All" && !sig.linkedScenarioIds.includes(f.scenario)) return false;
    if (f.category && f.category !== "All" && sig.category !== f.category) return false;
    if (f.strength && f.strength !== "All" && sig.currentStrength !== f.strength) return false;
    if (f.confidence && f.confidence !== "All" && sig.confidence !== f.confidence) return false;
    if (f.direction && f.direction !== "All" && sig.direction !== f.direction) return false;
    if (f.reviewDue && (!sig.nextReview || sig.nextReview > today)) return false;
    return true;
  });
  if (f.sort === "due") signals.sort((a, b) => String(a.nextReview || "9999").localeCompare(String(b.nextReview || "9999")));
  else if (f.sort === "newest") signals.sort((a, b) => String(b.lastReviewed).localeCompare(String(a.lastReviewed)));
  else signals.sort((a, b) => signalStrengthValue(b.currentStrength) - signalStrengthValue(a.currentStrength));
  return signals;
}

function renderWeakSignalBoard(compact = false) {
  const signals = compact ? state.weakSignals.slice(0, 6) : filteredWeakSignals();
  return `
    <section class="signal-board">
      ${signals.length ? signals.map(sig => `
        <article class="signal-card rich ${sig.id === state.ui.activeSignalId ? "active" : ""}">
          <button class="signal-open" data-action="activeSignal" data-id="${sig.id}">
            <span class="badge ${signalBadge(sig.currentStrength)}">${escapeHtml(sig.currentStrength)}</span>
            <h3>${escapeHtml(sig.title)}</h3>
            <p>${escapeHtml(sig.description || sig.evidence || "No description captured yet.")}</p>
          </button>
          <div class="signal-meta">
            <span>${escapeHtml(sig.category)}</span>
            <span>${escapeHtml(sig.confidence)} confidence</span>
            <span>${escapeHtml(sig.direction)}</span>
            <span>Review ${escapeHtml(sig.nextReview || "ad hoc")}</span>
          </div>
        </article>
      `).join("") : `<div class="empty">No signals match the current filters.</div>`}
    </section>
  `;
}

function signalBadge(strength) {
  if (strength === "Critical" || strength === "Strong") return "rose";
  if (strength === "Emerging") return "gold";
  if (strength === "Faint") return "blue";
  return "";
}

function renderWeakSignalDetail(sig) {
  if (!sig) return `<section class="panel"><div class="empty">Select or add a signal to edit its evidence, owner and review history.</div></section>`;
  return `
    <section class="panel signal-detail">
      <div class="inline-actions" style="justify-content:space-between">
        <h3>Signal Detail</h3>
        <div><button class="btn small" data-action="duplicateSignal" data-id="${sig.id}">Duplicate</button><button class="btn small danger" data-action="deleteSignal" data-id="${sig.id}">Delete</button></div>
      </div>
      <label>Title<textarea data-signal="${sig.id}" data-field="title">${escapeHtml(sig.title)}</textarea></label>
      <label>Description<textarea data-signal="${sig.id}" data-field="description">${escapeHtml(sig.description || "")}</textarea></label>
      <div class="grid two">
        <label>Category<select data-signal-select="${sig.id}" data-field="category">${signalCategories.map(v => `<option ${sig.category === v ? "selected" : ""}>${v}</option>`).join("")}</select></label>
        <label>Strength<select data-signal-select="${sig.id}" data-field="currentStrength">${signalStrengths.map(v => `<option ${sig.currentStrength === v ? "selected" : ""}>${v}</option>`).join("")}</select></label>
        <label>Confidence<select data-signal-select="${sig.id}" data-field="confidence">${signalConfidences.map(v => `<option ${sig.confidence === v ? "selected" : ""}>${v}</option>`).join("")}</select></label>
        <label>Direction<select data-signal-select="${sig.id}" data-field="direction">${signalDirections.map(v => `<option ${sig.direction === v ? "selected" : ""}>${v}</option>`).join("")}</select></label>
        <label>Owner<input data-signal="${sig.id}" data-field="owner" value="${escapeHtml(sig.owner || "")}"></label>
        <label>Cadence<select data-signal-select="${sig.id}" data-field="reviewCadence">${reviewCadences.map(v => `<option ${sig.reviewCadence === v ? "selected" : ""}>${v}</option>`).join("")}</select></label>
        <label>Last reviewed<input type="date" data-signal="${sig.id}" data-field="lastReviewed" value="${escapeHtml(sig.lastReviewed || "")}"></label>
        <label>Next review<input type="date" data-signal="${sig.id}" data-field="nextReview" value="${escapeHtml(sig.nextReview || "")}"></label>
      </div>
      <label>Evidence<textarea data-signal="${sig.id}" data-field="evidence">${escapeHtml(sig.evidence || "")}</textarea></label>
      <label>Source<input data-signal="${sig.id}" data-field="source" value="${escapeHtml(sig.source || "")}"></label>
      <label>Notes<textarea data-signal="${sig.id}" data-field="notes">${escapeHtml(sig.notes || "")}</textarea></label>
      <div class="scenario-link-list">
        <strong>Linked scenarios</strong>
        ${state.scenarios.map(sc => `<label class="check-line compact"><input type="checkbox" data-signal-link="${sig.id}" data-scenario="${sc.id}" ${sig.linkedScenarioIds.includes(sc.id) ? "checked" : ""}> ${escapeHtml(sc.name)}</label>`).join("")}
      </div>
      <form data-form="signalHistory" data-id="${sig.id}" class="history-form">
        <textarea name="evidence" placeholder="What changed since the last review?"></textarea>
        <input name="notes" placeholder="Review note">
        <button class="btn green small">Add update</button>
      </form>
      <div class="history-list">
        ${sig.history.length ? sig.history.map(h => `<div class="log-entry"><time>${escapeHtml(h.date)}</time><strong>${escapeHtml(h.strength)} / ${escapeHtml(h.confidence)} / ${escapeHtml(h.direction)}</strong><br>${escapeHtml(h.evidence || "")}<br>${escapeHtml(h.notes || "")}</div>`).join("") : `<div class="empty">No review history yet.</div>`}
      </div>
    </section>
  `;
}

function renderExport() {
  const view = state.ui.exportView || "report";
  return `
    <div class="grid">
      <section class="panel no-print">
        <h3>Export artefacts</h3>
        <div class="inline-actions">
          <button class="btn green" data-action="print">Print report</button>
          <button class="btn" data-action="exportJson">Export workshop data to JSON</button>
          <button class="btn" data-action="copySummary">Copy summary to clipboard</button>
          <button class="btn" data-action="copyMatrix">Copy scenario matrix</button>
          <button class="btn" data-action="copyActions">Copy actions table</button>
        </div>
        <div class="tabs" style="margin-top:1rem">
          ${[
            ["report", "Report"],
            ["presentation", "Presentation Summary"],
            ["recap", "Workshop Recap"],
            ["signals", "Signals Dashboard"],
            ["stress", "Stress Tests"],
            ["weakSignals", "Weak Signals"],
            ["portfolio", "Action Portfolio"],
            ["constellation", "Force Constellation"],
          ].map(([key, label]) => `<button class="tab ${view === key ? "active" : ""}" data-action="setExportView" data-view="${key}">${label}</button>`).join("")}
        </div>
      </section>
      <section class="report-view">${renderExportView(view)}</section>
    </div>
  `;
}

function renderExportView(view) {
  if (view === "presentation") return renderPresentationSummary();
  if (view === "recap") return renderWorkshopRecap();
  if (view === "signals") return renderSignalsDashboard();
  if (view === "stress") return `${renderStressPortfolio()}${renderStressHeatmap()}${renderStressReport()}`;
  if (view === "weakSignals") return `${renderScenarioWeatherMap()}${renderWeakSignalReport()}`;
  if (view === "portfolio") return renderActionPortfolio();
  if (view === "constellation") return renderForceConstellation();
  return reportHtml();
}

function renderPresentationSummary() {
  return `
    <div class="presentation-summary">
      <section class="slide-card"><span class="badge green">1</span><h2>${escapeHtml(state.setup.title)}</h2><p>${escapeHtml(selectedQuestion()?.text || state.setup.openingStatement)}</p></section>
      <section class="slide-card"><span class="badge blue">2</span><h2>Critical Uncertainties</h2><p>${escapeHtml(clusterById(state.axes.x?.clusterId)?.name || "Horizontal axis")} / ${escapeHtml(clusterById(state.axes.y?.clusterId)?.name || "Vertical axis")}</p></section>
      <section class="slide-card"><span class="badge gold">3</span><h2>Scenario Matrix</h2><div class="grid four">${state.scenarios.map(s => `<div class="mini-panel"><h3>${escapeHtml(s.name)}</h3><p>${escapeHtml(s.descriptor)}</p></div>`).join("")}</div></section>
      <section class="slide-card"><span class="badge rose">4</span><h2>Strategic Choices</h2>${renderActionPortfolio()}</section>
      <section class="slide-card"><span class="badge green">5</span><h2>Stress-Tested Strategies</h2>${renderStressHeatmap()}</section>
      <section class="slide-card"><span class="badge blue">6</span><h2>Signals to Watch</h2>${renderScenarioWeatherMap()}</section>
    </div>
  `;
}

function renderWorkshopRecap() {
  const robust = state.actions.filter(a => a.classification === "Robust action").length;
  return `
    <div class="recap-hero">
      <h2>Workshop Recap</h2>
      <p>We started with <strong>${state.drivingForces.length}</strong> forces, shaped <strong>${state.clusters.length}</strong> clusters, selected <strong>${state.axes.x?.clusterId && state.axes.y?.clusterId ? 2 : 0}</strong> critical uncertainties, built <strong>${state.scenarios.length}</strong> scenarios and tested <strong>${state.actions.length}</strong> actions.</p>
      <div class="recap-track">
        ${["Forces", "Clusters", "Axes", "Scenarios", "Actions"].map((label, i) => `<div class="recap-dot" style="--i:${i}"><strong>${[state.drivingForces.length, state.clusters.length, state.axes.x?.clusterId && state.axes.y?.clusterId ? 2 : 0, state.scenarios.length, state.actions.length][i]}</strong><span>${label}</span></div>`).join("")}
      </div>
      <p><strong>${robust}</strong> robust actions emerged for immediate consideration.</p>
    </div>
  `;
}

function renderSignalsDashboard() {
  const signals = state.scenarios.flatMap(sc => [
    ...(sc.fields.signs ? [{ scenario: sc.name, text: sc.fields.signs, type: "scenario sketch" }] : []),
    ...sc.events.filter(e => e.signal).map(e => ({ scenario: sc.name, text: e.signal, type: e.year || "timeline" })),
  ]);
  return `
    <div class="signals-board">
      <h2>Early Warning Indicators</h2>
      <div class="grid three">${signals.length ? signals.map(sig => `<article class="card signal-card"><span class="badge gold">${escapeHtml(sig.type)}</span><h3>${escapeHtml(sig.scenario)}</h3><p>${escapeHtml(sig.text)}</p></article>`).join("") : `<div class="empty">Add early signs in scenario sketches or timeline events.</div>`}</div>
      <h2>What to Monitor</h2>
      <p>${escapeHtml(state.implications?.monitor || "No monitoring implications captured yet.")}</p>
    </div>
  `;
}

function renderActionPortfolio() {
  const maxEffort = 5;
  return `
    <div class="portfolio-map">
      <div class="portfolio-axis y">More robust</div>
      <div class="portfolio-canvas">
        ${state.actions.length ? state.actions.map(a => {
          const useful = Object.values(a.ratings || {}).filter(v => v === "strongly useful" || v === "useful").length;
          const left = Math.min(88, Math.max(8, (Number(a.effort || 1) / maxEffort) * 88));
          const bottom = Math.min(84, Math.max(12, useful * 20 + Number(a.confidence || 1) * 4));
          return `<div class="portfolio-point ${classBadge(a.classification)}" style="left:${left}%;bottom:${bottom}%"><strong>${escapeHtml(a.title)}</strong><span>${escapeHtml(a.classification)}</span></div>`;
        }).join("") : `<div class="empty">Add strategic actions to build the portfolio.</div>`}
      </div>
      <div></div><div class="portfolio-axis">More effort</div>
    </div>
  `;
}

function renderForceConstellation() {
  const clusters = state.clusters.length ? state.clusters : [makeCluster("Unclustered", state.drivingForces.map(f => f.id))];
  return `
    <div class="constellation">
      <h2>Force Constellation</h2>
      <div class="constellation-grid">${clusters.map((c, i) => `
        <section class="constellation-cluster" style="--hue:${(i * 47) % 360}">
          <h3>${escapeHtml(c.name)}</h3>
          ${c.forceIds.map(id => forceById(id)).filter(Boolean).map(f => `<span class="force-node">${escapeHtml(f.title)}</span>`).join("") || `<span class="force-node">No forces yet</span>`}
        </section>
      `).join("")}</div>
    </div>
  `;
}

function renderStressReport() {
  return `
    <section class="panel">
      <h2>Stress-Test Theatre Notes</h2>
      ${state.stressTests.length ? state.stressTests.map(test => `
        <article class="report-block">
          <h3>${escapeHtml(test.actionTitle)}</h3>
          <p><strong>Classification:</strong> ${escapeHtml(test.overallClassification || "Unclassified")} | <strong>Recommendation:</strong> ${escapeHtml(test.decisionRecommendation || "")}</p>
          <p>${escapeHtml(test.actionDescription || "")}</p>
          <p><strong>Adaptation summary:</strong> ${escapeHtml(test.adaptationSummary || "Not captured.")}</p>
          <div class="grid two">${state.scenarios.map(sc => {
            const result = test.scenarioResults.find(r => r.scenarioId === sc.id) || makeStressResult(sc.id);
            return `<div class="mini-panel"><h4>${escapeHtml(sc.name)}</h4><p><strong>${escapeHtml(result.resultLabel)}</strong> (${stressViability(result)}/5 viability)</p><p>${escapeHtml(result.whatHappens || "")}</p><p><em>Adaptation:</em> ${escapeHtml(result.adaptationNeeded || "None captured.")}</p><p><em>Signals:</em> ${escapeHtml(result.earlyWarningSignals || "None captured.")}</p></div>`;
          }).join("")}</div>
        </article>
      `).join("") : `<div class="empty">No stress tests captured.</div>`}
    </section>
  `;
}

function renderWeakSignalReport() {
  return `
    <section class="panel">
      <h2>Weak Signals Monitor</h2>
      ${state.weakSignals.length ? `<table class="testing-table"><thead><tr><th>Signal</th><th>Linked scenarios</th><th>Strength</th><th>Confidence</th><th>Direction</th><th>Owner / review</th></tr></thead><tbody>
        ${state.weakSignals.map(sig => `<tr>
          <td><strong>${escapeHtml(sig.title)}</strong><br>${escapeHtml(sig.evidence || sig.description || "")}</td>
          <td>${sig.linkedScenarioIds.map(id => state.scenarios.find(sc => sc.id === id)?.name).filter(Boolean).map(escapeHtml).join(", ") || "Unlinked"}</td>
          <td>${escapeHtml(sig.currentStrength)}</td>
          <td>${escapeHtml(sig.confidence)}</td>
          <td>${escapeHtml(sig.direction)}</td>
          <td>${escapeHtml(sig.owner || "TBC")}<br>${escapeHtml(sig.nextReview || "Ad hoc")}</td>
        </tr>`).join("")}
      </tbody></table>` : `<div class="empty">No weak signals captured.</div>`}
    </section>
  `;
}

function reportHtml() {
  const selected = selectedQuestion();
  const robustGroups = ["Robust action", "Contingent action", "Hedging action", "Fragile action", "Stop / avoid"];
  const x = hydrateAxis(state.axes.x);
  const y = hydrateAxis(state.axes.y);
  return `
    <h1>${escapeHtml(state.setup.title)}</h1>
    <p><strong>Organisation:</strong> ${escapeHtml(state.setup.organisation)} | <strong>Facilitator:</strong> ${escapeHtml(state.setup.facilitator)} | <strong>Date:</strong> ${escapeHtml(state.setup.date)}</p>
    <p><strong>Focal question:</strong> ${escapeHtml(selected?.text || state.setup.openingStatement)}</p>
    <p><strong>Time horizon:</strong> ${escapeHtml(state.setup.timeHorizon)} | <strong>Participants:</strong> ${escapeHtml(state.setup.participants)}</p>
    <p><strong>Desired final output:</strong> ${escapeHtml(state.setup.desiredOutput)}</p>
    <h2>Driving Forces</h2><ul>${state.drivingForces.map(f => `<li><strong>${escapeHtml(f.title)}</strong> (${escapeHtml(f.category)})<br>${escapeHtml(f.description || "")}${f.evidence ? `<br><em>Evidence:</em> ${escapeHtml(f.evidence)}` : ""}${f.notes ? `<br><em>Notes:</em> ${escapeHtml(f.notes)}` : ""}</li>`).join("")}</ul>
    <h2>Clusters and Plausible Extremes</h2>${state.clusters.map(c => `<h3>${escapeHtml(c.name)}</h3><p>${escapeHtml(c.description || "")}</p><p><strong>Causal logic:</strong> ${escapeHtml(c.causalNotes || "Not captured.")}</p><p><strong>Open questions:</strong> ${escapeHtml(c.openQuestions || "None captured.")}</p><ul><li>${escapeHtml(c.extremes.a.label)}: ${escapeHtml(c.extremes.a.description)} ${c.extremes.a.visible ? `<br><em>Visible:</em> ${escapeHtml(c.extremes.a.visible)}` : ""}</li><li>${escapeHtml(c.extremes.b.label)}: ${escapeHtml(c.extremes.b.description)} ${c.extremes.b.visible ? `<br><em>Visible:</em> ${escapeHtml(c.extremes.b.visible)}` : ""}</li></ul>`).join("")}
    <h2>Prioritisation Results</h2><ol>${[...state.clusters].sort((a,b)=>clusterPriority(b)-clusterPriority(a)).map(c => `<li>${escapeHtml(c.name)}: impact ${c.impact}, uncertainty ${c.uncertainty}</li>`).join("")}</ol>
    <h2>Selected Scenario Axes</h2><p><strong>${escapeHtml(clusterById(x.clusterId)?.name || "Horizontal axis missing")}:</strong> ${escapeHtml(x.low || "Low")} to ${escapeHtml(x.high || "High")}</p><p><strong>${escapeHtml(clusterById(y.clusterId)?.name || "Vertical axis missing")}:</strong> ${escapeHtml(y.low || "Low")} to ${escapeHtml(y.high || "High")}</p>
    <h2>Scenario Matrix and Narratives</h2>${state.scenarios.map(s => `<h3>${escapeHtml(s.name)}</h3><p>${escapeHtml(s.descriptor || "")}</p><p><strong>World feel:</strong> ${escapeHtml(s.fields.feel || "")}</p><p><strong>Changed:</strong> ${escapeHtml(s.fields.changed || "")}</p><p><strong>Risks:</strong> ${escapeHtml(s.fields.risks || "")}</p><p><strong>Opportunities:</strong> ${escapeHtml(s.fields.opportunities || "")}</p><p><strong>Early warning indicators:</strong> ${escapeHtml(s.fields.signs || "")}</p><ul>${s.events.map(e => `<li>${escapeHtml(e.year)}: ${escapeHtml(e.title)} - ${escapeHtml(e.description)}<br><em>Cause:</em> ${escapeHtml(e.cause || "")}<br><em>Consequence:</em> ${escapeHtml(e.consequence || "")}<br><em>Signal:</em> ${escapeHtml(e.signal || "")}</li>`).join("")}</ul><p><strong>Critique notes:</strong> ${s.critiques.map(c => `${c.status}: ${c.text}`).map(escapeHtml).join("; ") || "None captured."}</p>`).join("")}
    <h2>Action Testing Matrix</h2><table><thead><tr><th>Action</th>${state.scenarios.map(s => `<th>${escapeHtml(s.name)}</th>`).join("")}<th>Classification</th></tr></thead><tbody>${state.actions.map(a => `<tr><td>${escapeHtml(a.title)}</td>${state.scenarios.map(s => `<td>${escapeHtml(a.ratings[s.id] || "uncertain")}</td>`).join("")}<td>${escapeHtml(a.classification)}</td></tr>`).join("")}</tbody></table>
    <h2>Strategic Implications</h2><p><strong>Start:</strong> ${escapeHtml(state.implications?.start || "")}</p><p><strong>Stop:</strong> ${escapeHtml(state.implications?.stop || "")}</p><p><strong>Protect:</strong> ${escapeHtml(state.implications?.protect || "")}</p><p><strong>Monitor:</strong> ${escapeHtml(state.implications?.monitor || "")}</p><p><strong>Decide now:</strong> ${escapeHtml(state.implications?.decideNow || "")}</p><p><strong>Defer:</strong> ${escapeHtml(state.implications?.defer || "")}</p>${robustGroups.map(g => `<h3>${g}</h3><ul>${state.actions.filter(a => a.classification === g).map(a => `<li>${escapeHtml(a.title)} - ${escapeHtml(a.description)}<br>Owner: ${escapeHtml(a.owner || "TBC")} | Timeframe: ${escapeHtml(a.timeframe || "TBC")} | Next decision: ${escapeHtml(a.nextDecision || "TBC")}</li>`).join("") || "<li>None captured.</li>"}</ul>`).join("")}
    <h2>Scenario Stress Tests</h2>${state.stressTests.map(test => `<h3>${escapeHtml(test.actionTitle)}</h3><p><strong>${escapeHtml(test.overallClassification || "Unclassified")}:</strong> ${escapeHtml(test.decisionRecommendation || "")}</p><p>${escapeHtml(test.adaptationSummary || test.overallNotes || "")}</p><ul>${state.scenarios.map(sc => { const result = test.scenarioResults.find(r => r.scenarioId === sc.id) || makeStressResult(sc.id); return `<li><strong>${escapeHtml(sc.name)}:</strong> ${escapeHtml(result.resultLabel)}. ${escapeHtml(result.whatHappens || "")} <em>Adaptation:</em> ${escapeHtml(result.adaptationNeeded || "")}</li>`; }).join("")}</ul>`).join("") || "<p>No stress tests captured.</p>"}
    <h2>Weak Signals Monitor</h2>${state.scenarios.map(sc => { const activation = scenarioActivation(sc.id); return `<h3>${escapeHtml(sc.name)}: ${activation.activationScore}% ${escapeHtml(activation.label)}</h3><ul>${state.weakSignals.filter(sig => sig.linkedScenarioIds.includes(sc.id)).map(sig => `<li><strong>${escapeHtml(sig.title)}</strong> - ${escapeHtml(sig.currentStrength)}, ${escapeHtml(sig.confidence)} confidence, ${escapeHtml(sig.direction)}. Evidence: ${escapeHtml(sig.evidence || "")}. Next review: ${escapeHtml(sig.nextReview || "Ad hoc")}</li>`).join("") || "<li>No linked signals.</li>"}</ul>`; }).join("")}
    <h2>Minority Reports</h2><ul>${state.minorityReports.map(m => `<li>${escapeHtml(m.text)}</li>`).join("") || "<li>None captured.</li>"}</ul>
    <h2>Parking Lot</h2><ul>${state.parkingLot.map(p => `<li>${escapeHtml(p.text)}</li>`).join("")}</ul>
    <h2>Decision Log</h2><ul>${state.decisionLog.map(d => `<li>${new Date(d.createdAt).toLocaleString()}: ${escapeHtml(d.text)}</li>`).join("")}</ul>
  `;
}

function bindEvents(root) {
  root.addEventListener("click", handleClick);
  root.addEventListener("input", handleInput);
  root.addEventListener("change", handleChange);
  root.addEventListener("submit", handleSubmit);
  root.addEventListener("keydown", handleKeydown);
  root.addEventListener("dragstart", handleDragStart);
  root.addEventListener("dragover", handleDragOver);
  root.addEventListener("dragleave", handleDragLeave);
  root.addEventListener("drop", handleDrop);
  root.addEventListener("blur", handleBlur, true);
}

function handleClick(e) {
  const stepBtn = e.target.closest("[data-step]");
  if (stepBtn) return setState(s => { s.currentStep = Number(stepBtn.dataset.step); });
  const btn = e.target.closest("[data-action]");
  if (!btn) return;
  const action = btn.dataset.action;
  const id = btn.dataset.id;
  if (action === "undo") return undo();
  if (action === "toggleCommands") return setState(s => { s.ui.commandOpen = !s.ui.commandOpen; }, { undo: false });
  if (action === "toggleGuided") return setState(s => { s.ui.guidedMode = !s.ui.guidedMode; }, { undo: false });
  if (action === "toggleGlossary") return setState(s => { s.ui.glossaryOpen = !s.ui.glossaryOpen; }, { undo: false });
  if (action === "commandStep") return setState(s => { s.currentStep = Number(btn.dataset.value); s.ui.commandOpen = false; }, { undo: false });
  if (action === "toggleRoom") return setState(s => { s.ui.roomMode = !s.ui.roomMode; s.ui.commandOpen = false; }, { undo: false });
  if (action === "next") return setState(s => { s.currentStep = Math.min(steps.length - 1, s.currentStep + 1); });
  if (action === "prev") return setState(s => { s.currentStep = Math.max(0, s.currentStep - 1); });
  if (action === "save") return saveToast("Saved to local storage.");
  if (action === "loadSample") return setState(s => Object.assign(s, sampleWorkshop()));
  if (action === "loadSaved") return setState(s => Object.assign(s, loadState() || s));
  if (action === "reset" && confirm("Reset this workshop?")) return setState(s => Object.assign(s, createEmptyWorkshop()));
  if (action === "exportJson") return downloadJson();
  if (action === "importJson") return importJson();
  if (action === "selectFocal") return setState(s => { s.focalQuestions.forEach(q => q.selected = q.id === id); logDecision(s, `Selected focal question: ${s.focalQuestions.find(q => q.id === id)?.text}`); });
  if (action === "deleteFocal") return setState(s => { s.focalQuestions = s.focalQuestions.filter(q => q.id !== id); });
  if (action === "deleteForce") return setState(s => { s.drivingForces = s.drivingForces.filter(f => f.id !== id); s.clusters.forEach(c => c.forceIds = c.forceIds.filter(fid => fid !== id)); });
  if (action === "seedFocal") return setState(s => seedFocalQuestion(s));
  if (action === "duplicateForce") return setState(s => duplicateForceIntoCluster(s, id, btn.dataset.cluster));
  if (action === "parkForce") return setState(s => parkForce(s, id));
  if (action === "addCluster") return setState(s => { s.clusters.push(makeCluster()); logDecision(s, "Created a new cluster area."); });
  if (action === "deleteCluster") return setState(s => { s.clusters = s.clusters.filter(c => c.id !== id); });
  if (action === "recommendAxes") return setState(s => recommendAxes(s));
  if (action === "pairwiseWin") return setState(s => pairwiseWin(s, btn.dataset.kind, id));
  if (action === "resetPairwise") return setState(s => { s.pairwise[btn.dataset.kind] = []; if (btn.dataset.kind === "impact") s.pairwise.cursorImpact = 0; else s.pairwise.cursorUncertainty = 0; });
  if (action === "swapAxes") return setState(s => { [s.axes.x, s.axes.y] = [s.axes.y, s.axes.x]; logDecision(s, "Swapped scenario matrix axes."); });
  if (action === "reverseX") return setState(s => reverseAxis(s, "x"));
  if (action === "reverseY") return setState(s => reverseAxis(s, "y"));
  if (action === "activeScenario") return setState(() => { activeScenarioId = id; });
  if (action === "addEvent") return setState(s => { s.scenarios.find(sc => sc.id === id)?.events.push({ id: uid("event"), title: "New event", year: s.setup.date?.slice(0, 4) || "2026", description: "", cause: "", consequence: "", stakeholders: "", signal: "", plausibility: "" }); });
  if (action === "deleteEvent") return setState(s => s.scenarios.forEach(sc => sc.events = sc.events.filter(ev => ev.id !== id)));
  if (action === "deleteCritique") return setState(s => { const sc = s.scenarios.find(x => x.id === btn.dataset.scenario); if (sc) sc.critiques = sc.critiques.filter(n => n.id !== id); });
  if (action === "deleteAction") return setState(s => { s.actions = s.actions.filter(a => a.id !== id); });
  if (action === "activeStress") return setState(s => { s.ui.activeStressId = id; }, { undo: false });
  if (action === "duplicateStress") return setState(s => {
    const original = s.stressTests.find(t => t.id === id);
    if (original) {
      const copy = JSON.parse(JSON.stringify(original));
      copy.id = uid("stress");
      copy.actionTitle = `${copy.actionTitle} copy`;
      copy.createdAt = new Date().toISOString();
      s.stressTests.push(copy);
      s.ui.activeStressId = copy.id;
    }
  });
  if (action === "deleteStress") return setState(s => { s.stressTests = s.stressTests.filter(t => t.id !== id); s.ui.activeStressId = s.stressTests[0]?.id; });
  if (action === "activeSignal") return setState(s => { s.ui.activeSignalId = id; }, { undo: false });
  if (action === "addSignal") return setState(s => { const sig = makeWeakSignal("New weak signal", []); s.weakSignals.unshift(sig); s.ui.activeSignalId = sig.id; });
  if (action === "duplicateSignal") return setState(s => {
    const original = s.weakSignals.find(sig => sig.id === id);
    if (original) {
      const copy = JSON.parse(JSON.stringify(original));
      copy.id = uid("signal");
      copy.title = `${copy.title} copy`;
      s.weakSignals.unshift(copy);
      s.ui.activeSignalId = copy.id;
    }
  });
  if (action === "deleteSignal") return setState(s => { s.weakSignals = s.weakSignals.filter(sig => sig.id !== id); s.ui.activeSignalId = s.weakSignals[0]?.id; });
  if (action === "importScenarioSignals") return setState(s => importScenarioSignals(s));
  if (action === "deleteParking") return setState(s => { s.parkingLot = s.parkingLot.filter(p => p.id !== id); });
  if (action === "timerStart") return startTimer();
  if (action === "timerReset") return resetTimer();
  if (action === "print") return window.print();
  if (action === "copySummary") return copyText(summaryText());
  if (action === "copyMatrix") return copyText(matrixText());
  if (action === "copyActions") return copyText(actionsText());
  if (action === "setExportView") return setState(s => { s.ui.exportView = btn.dataset.view; }, { undo: false });
}

function handleInput(e) {
  const el = e.target;
  if (el.dataset.setup) return updateQuietly(s => { s.setup[el.dataset.setup] = el.value; });
  if (el.dataset.focalScore) return setState(s => { const q = s.focalQuestions.find(q => q.id === el.dataset.focalScore); if (q) q.scores[el.dataset.scoreKey] = Number(el.value); });
  if (el.dataset.focalText) return updateQuietly(s => { const q = s.focalQuestions.find(q => q.id === el.dataset.focalText); if (q) q.text = el.value; });
  if (el.dataset.selectedQuestion) return updateQuietly(() => { const q = selectedQuestion(); if (q) q.text = el.value; });
  if (el.dataset.cluster) return updateQuietly(s => { const c = s.clusters.find(c => c.id === el.dataset.cluster); if (c) c[el.dataset.field] = el.value; });
  if (el.dataset.extreme) return updateQuietly(s => { const c = s.clusters.find(c => c.id === el.dataset.extreme); if (c) c.extremes[el.dataset.side][el.dataset.field] = el.value; });
  if (el.dataset.clusterScore) return setState(s => { const c = s.clusters.find(c => c.id === el.dataset.clusterScore); if (c) c[el.dataset.scoreKey] = Number(el.value); });
  if (el.dataset.scenario) return updateQuietly(s => { const sc = s.scenarios.find(sc => sc.id === el.dataset.scenario); if (sc) sc[el.dataset.field] = el.value; });
  if (el.dataset.scenarioField) return updateQuietly(s => { const sc = s.scenarios.find(sc => sc.id === el.dataset.scenarioField); if (sc) sc.fields[el.dataset.field] = el.value; });
  if (el.dataset.event) return updateQuietly(s => s.scenarios.forEach(sc => { const ev = sc.events.find(ev => ev.id === el.dataset.event); if (ev) ev[el.dataset.field] = el.value; }));
  if (el.dataset.actionEdit) return updateQuietly(s => { const a = s.actions.find(a => a.id === el.dataset.actionEdit); if (a) a[el.dataset.field] = el.value; });
  if (el.dataset.actionRange) return setState(s => { const a = s.actions.find(a => a.id === el.dataset.actionRange); if (a) { a[el.dataset.field] = Number(el.value); classifyAction(a); } });
  if (el.dataset.implication) return updateQuietly(s => { s.implications ||= {}; s.implications[el.dataset.implication] = el.value; });
  if (el.dataset.axisEndpoint) return updateQuietly(s => { s.axes[el.dataset.axisEndpoint] ||= {}; s.axes[el.dataset.axisEndpoint][el.dataset.field] = el.value; s.axes[el.dataset.axisEndpoint].sync = false; });
  if (el.dataset.stress) return updateQuietly(s => { const t = s.stressTests.find(t => t.id === el.dataset.stress); if (t) t[el.dataset.field] = el.value; });
  if (el.dataset.stressResult) return updateQuietly(s => {
    const t = s.stressTests.find(t => t.id === el.dataset.stressResult);
    const r = t?.scenarioResults.find(r => r.scenarioId === el.dataset.result);
    if (r) r[el.dataset.field] = el.value;
  });
  if (el.dataset.stressRange) return setState(s => {
    const t = s.stressTests.find(t => t.id === el.dataset.stressRange);
    const r = t?.scenarioResults.find(r => r.scenarioId === el.dataset.result);
    if (r) {
      r[el.dataset.field] = Number(el.value);
      r.resultLabel = stressResultLabel(r);
      updateStressTestClassification(t);
    }
  });
  if (el.dataset.signal) return updateQuietly(s => {
    const sig = s.weakSignals.find(sig => sig.id === el.dataset.signal);
    if (sig) {
      sig[el.dataset.field] = el.value;
      if (el.dataset.field === "lastReviewed") sig.nextReview = nextReviewDate(sig.lastReviewed, sig.reviewCadence);
    }
  });
}

function updateQuietly(mutator) {
  mutator(state);
  syncSelectedAxisEndpoints();
  saveState();
}

function handleChange(e) {
  const el = e.target;
  if (el.dataset.axis) return setState(s => {
    const c = clusterById(el.value);
    s.axes[el.dataset.axis] = c ? { clusterId: c.id, low: c.extremes.a.label, high: c.extremes.b.label, sync: true } : null;
    if (c) logDecision(s, `Selected ${el.dataset.axis.toUpperCase()} scenario axis: ${c.name}`);
  });
  if (el.dataset.actionRating) return setState(s => {
    const a = s.actions.find(a => a.id === el.dataset.actionRating);
    if (a) { a.ratings[el.dataset.scenario] = el.value; classifyAction(a); logDecision(s, `Classified action "${a.title}" as ${a.classification}.`); }
  });
  if (el.dataset.critiqueStatus) return setState(s => {
    const sc = s.scenarios.find(sc => sc.id === el.dataset.critiqueStatus);
    const n = sc?.critiques.find(n => n.id === el.dataset.id);
    if (n) n.status = el.value;
  });
  if (el.dataset.stressSelect) return setState(s => {
    const t = s.stressTests.find(t => t.id === el.dataset.stressSelect);
    if (t) {
      t[el.dataset.field] = el.value;
      if (el.dataset.field === "overallClassification") t.decisionRecommendation = recommendationForClassification(el.value);
      updateStressTestClassification(t);
      logDecision(s, `Stress-tested "${t.actionTitle}" as ${t.overallClassification}.`);
    }
  });
  if (el.dataset.stressResultSelect) return setState(s => {
    const t = s.stressTests.find(t => t.id === el.dataset.stressResultSelect);
    const r = t?.scenarioResults.find(r => r.scenarioId === el.dataset.result);
    if (r) {
      r[el.dataset.field] = el.value;
      updateStressTestClassification(t);
    }
  });
  if (el.dataset.signalSelect) return setState(s => {
    const sig = s.weakSignals.find(sig => sig.id === el.dataset.signalSelect);
    if (sig) {
      sig[el.dataset.field] = el.value;
      if (el.dataset.field === "reviewCadence") sig.nextReview = nextReviewDate(sig.lastReviewed, sig.reviewCadence);
    }
  });
  if (el.dataset.signalFilter) return setState(s => {
    s.signalFilters ||= {};
    s.signalFilters[el.dataset.signalFilter] = el.type === "checkbox" ? el.checked : el.value;
  }, { undo: false });
  if (el.dataset.signalLink) return setState(s => {
    const sig = s.weakSignals.find(sig => sig.id === el.dataset.signalLink);
    if (!sig) return;
    if (el.checked && !sig.linkedScenarioIds.includes(el.dataset.scenario)) sig.linkedScenarioIds.push(el.dataset.scenario);
    if (!el.checked) sig.linkedScenarioIds = sig.linkedScenarioIds.filter(id => id !== el.dataset.scenario);
  });
}

function handleSubmit(e) {
  e.preventDefault();
  const form = e.target;
  const data = Object.fromEntries(new FormData(form).entries());
  if (form.dataset.form === "focal" && data.text) {
    setState(s => s.focalQuestions.push({ id: uid("fq"), text: data.text, scores: { relevance: 3, uncertainty: 3, scope: 3, actionability: 3, usefulness: 3 } }));
  }
  if (form.dataset.form === "force" && data.title) {
    setState(s => s.drivingForces.unshift({ id: uid("force"), title: data.title, description: data.description || "", category: data.category || "Other", notes: data.notes || "", evidence: data.evidence || "" }));
  }
  if (form.dataset.form === "parking" && data.text) {
    setState(s => s.parkingLot.unshift({ id: uid("park"), text: data.text, category: data.category || "parking", sourceStep: s.currentStep, createdAt: new Date().toISOString() }));
  }
  if (form.dataset.form === "minority" && data.text) {
    setState(s => s.minorityReports.unshift({ id: uid("minority"), text: data.text, sourceStep: s.currentStep, createdAt: new Date().toISOString() }));
  }
  if (form.dataset.form === "critique" && data.text) {
    setState(s => {
      const sc = s.scenarios.find(sc => sc.id === form.dataset.id);
      sc?.critiques.unshift({ id: uid("critique"), text: `${data.prompt} ${data.text}`, status: "accepted" });
    });
  }
  if (form.dataset.form === "action" && data.title) {
    setState(s => {
      const a = makeAction(data.title, data.description || "");
      a.owner = data.owner || ""; a.timeframe = data.timeframe || ""; a.nextDecision = data.nextDecision || ""; a.effort = Number(data.effort || 2); a.confidence = Number(data.confidence || 3);
      s.scenarios.forEach(sc => a.ratings[sc.id] = "uncertain");
      classifyAction(a);
      s.actions.push(a);
    });
  }
  if (form.dataset.form === "stress") {
    setState(s => {
      const source = s.actions.find(a => a.id === data.sourceAction);
      const title = data.title || source?.title || "New strategy under test";
      const test = makeStressTest(title, source?.description || "", s.scenarios);
      if (source) {
        test.owner = source.owner || "";
        test.timeframe = source.timeframe || "";
      }
      s.stressTests.push(test);
      s.ui.activeStressId = test.id;
      logDecision(s, `Added strategy stress test: ${test.actionTitle}.`);
    });
  }
  if (form.dataset.form === "signalHistory") {
    setState(s => {
      const sig = s.weakSignals.find(sig => sig.id === form.dataset.id);
      if (sig) {
        const today = new Date().toISOString().slice(0, 10);
        sig.lastReviewed = today;
        sig.nextReview = nextReviewDate(today, sig.reviewCadence);
        sig.history.unshift({ id: uid("history"), date: today, strength: sig.currentStrength, confidence: sig.confidence, direction: sig.direction, evidence: data.evidence || sig.evidence || "", notes: data.notes || "" });
      }
    });
  }
  form.reset();
}

function handleKeydown(e) {
  if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === "k") {
    e.preventDefault();
    return setState(s => { s.ui.commandOpen = !s.ui.commandOpen; }, { undo: false });
  }
  if (e.key === "Escape" && state.ui.commandOpen) {
    return setState(s => { s.ui.commandOpen = false; }, { undo: false });
  }
  if (e.key === "Escape" && state.ui.glossaryOpen) {
    return setState(s => { s.ui.glossaryOpen = false; }, { undo: false });
  }
  const form = e.target.closest('form[data-form="force"]');
  if (!form) return;
  if (e.key === "Escape") form.reset();
  if (e.key === "Enter" && !e.shiftKey && e.target.tagName === "TEXTAREA") {
    e.preventDefault();
    form.requestSubmit();
  }
}

function handleBlur(e) {
  const el = e.target;
  if (el.dataset.editForce) {
    setState(s => { const f = s.drivingForces.find(f => f.id === el.dataset.editForce); if (f) f[el.dataset.field] = el.textContent.trim(); });
  }
  if (el.dataset.critique) {
    setState(s => { const sc = s.scenarios.find(sc => sc.id === el.dataset.critique); const n = sc?.critiques.find(n => n.id === el.dataset.id); if (n) n.text = el.textContent.trim(); });
  }
}

function handleDragStart(e) {
  const force = e.target.closest("[data-force-id]");
  const cluster = e.target.closest("[data-cluster-card]");
  const event = e.target.closest("[data-event-id]");
  if (force) { draggedForceId = force.dataset.forceId; e.dataTransfer.setData("text/force", draggedForceId); }
  if (cluster) e.dataTransfer.setData("text/cluster", cluster.dataset.clusterCard);
  if (event) { draggedEventId = event.dataset.eventId; e.dataTransfer.setData("text/event", draggedEventId); }
}

function handleDragOver(e) {
  const drop = e.target.closest("[data-cluster-drop], [data-drop-unclustered], [data-matrix-quadrant], [data-event-id], .timeline");
  if (drop) { e.preventDefault(); drop.classList.add("drag-over"); }
}

function handleDragLeave(e) {
  const drop = e.target.closest("[data-cluster-drop], [data-drop-unclustered], [data-matrix-quadrant], [data-event-id], .timeline");
  drop?.classList.remove("drag-over");
}

function handleDrop(e) {
  const clusterDrop = e.target.closest("[data-cluster-drop]");
  const unclustered = e.target.closest("[data-drop-unclustered]");
  const quadrant = e.target.closest("[data-matrix-quadrant]");
  const eventDrop = e.target.closest("[data-event-id]");
  if (clusterDrop && draggedForceId) {
    e.preventDefault();
    setState(s => {
      s.clusters.forEach(c => c.forceIds = c.forceIds.filter(id => id !== draggedForceId));
      const c = s.clusters.find(c => c.id === clusterDrop.dataset.clusterDrop);
      if (c && !c.forceIds.includes(draggedForceId)) c.forceIds.push(draggedForceId);
    });
  }
  if (unclustered && draggedForceId) {
    e.preventDefault();
    setState(s => s.clusters.forEach(c => c.forceIds = c.forceIds.filter(id => id !== draggedForceId)));
  }
  if (quadrant) {
    const id = e.dataTransfer.getData("text/cluster");
    const c = clusterById(id);
    if (c) {
      const q = Number(quadrant.dataset.matrixQuadrant);
      setState(() => {
        c.impact = q < 2 ? 5 : 2;
        c.uncertainty = q === 1 || q === 3 ? 5 : 2;
      });
    }
  }
  if (draggedEventId && eventDrop && eventDrop.dataset.eventId !== draggedEventId) {
    e.preventDefault();
    setState(s => reorderEvent(s, draggedEventId, eventDrop.dataset.eventId));
  }
  draggedForceId = null;
  draggedEventId = null;
}

function reorderEvent(s, draggedId, targetId) {
  for (const sc of s.scenarios) {
    const from = sc.events.findIndex(ev => ev.id === draggedId);
    const to = sc.events.findIndex(ev => ev.id === targetId);
    if (from === -1 || to === -1) continue;
    const [item] = sc.events.splice(from, 1);
    sc.events.splice(to, 0, item);
    logDecision(s, `Reordered timeline event in "${sc.name}".`);
    return;
  }
}

function recommendAxes(s) {
  const [x, y] = [...s.clusters].sort((a, b) => clusterPriority(b) - clusterPriority(a));
  if (x) s.axes.x = { clusterId: x.id, low: x.extremes.a.label, high: x.extremes.b.label, sync: true };
  if (y) s.axes.y = { clusterId: y.id, low: y.extremes.a.label, high: y.extremes.b.label, sync: true };
  if (x && y) logDecision(s, `Recommended axes selected: ${x.name} and ${y.name}.`);
}

function seedFocalQuestion(s) {
  const issue = (s.setup.focalIssue || "this focal issue").trim();
  const horizon = (s.setup.timeHorizon || "the chosen horizon").trim();
  const output = (s.setup.desiredOutput || "our choices now").replace(/\.$/, "").trim();
  const text = `How might ${issue} evolve by ${horizon}, and what would this mean for ${output.toLowerCase()}?`;
  const existing = s.focalQuestions.find(q => q.text === text);
  if (existing) {
    s.focalQuestions.forEach(q => q.selected = q.id === existing.id);
  } else {
    s.focalQuestions.unshift({ id: uid("fq"), text, selected: true, scores: { relevance: 4, uncertainty: 4, scope: 3, actionability: 4, usefulness: 4 } });
    s.focalQuestions.slice(1).forEach(q => q.selected = false);
  }
  logDecision(s, `Seeded focal question from setup: ${text}`);
}

function duplicateForceIntoCluster(s, forceId, clusterId) {
  const force = s.drivingForces.find(f => f.id === forceId);
  const cluster = s.clusters.find(c => c.id === clusterId);
  if (!force || !cluster) return;
  const copy = { ...force, id: uid("force"), title: `${force.title} (duplicate)` };
  s.drivingForces.unshift(copy);
  cluster.forceIds.push(copy.id);
  logDecision(s, `Duplicated force into cluster "${cluster.name}".`);
}

function parkForce(s, forceId) {
  const force = s.drivingForces.find(f => f.id === forceId);
  if (!force) return;
  s.parkingLot.unshift({ id: uid("park"), text: force.title, category: "parking", sourceStep: s.currentStep, createdAt: new Date().toISOString() });
  s.clusters.forEach(c => c.forceIds = c.forceIds.filter(id => id !== forceId));
  logDecision(s, `Parked force: ${force.title}`);
}

function pairwiseWin(s, kind, id) {
  const pairs = makePairs(s.clusters);
  const cursorKey = kind === "impact" ? "cursorImpact" : "cursorUncertainty";
  const completed = new Set(s.pairwise[kind] || []);
  const remainingPairs = pairs.filter(pair => !completed.has(pairKey(pair)));
  const currentPair = remainingPairs[(s.pairwise[cursorKey] || 0) % Math.max(1, remainingPairs.length)];
  const c = s.clusters.find(c => c.id === id);
  if (!c) return;
  if (currentPair) s.pairwise[kind] = [...completed, pairKey(currentPair)];
  if (kind === "impact") { c.impactWins += 1; s.pairwise.cursorImpact += 1; }
  else { c.uncertaintyWins += 1; s.pairwise.cursorUncertainty += 1; }
}

function reverseAxis(s, axis) {
  if (!s.axes[axis]) return;
  [s.axes[axis].low, s.axes[axis].high] = [s.axes[axis].high, s.axes[axis].low];
  s.axes[axis].sync = false;
  logDecision(s, `Reversed ${axis.toUpperCase()} axis endpoints.`);
}

function classifyAction(a) {
  const vals = Object.values(a.ratings || {});
  const useful = vals.filter(v => v === "strongly useful" || v === "useful").length;
  const bad = vals.filter(v => v === "risky" || v === "harmful").length;
  const neutral = vals.filter(v => v === "neutral" || v === "uncertain").length;
  if (bad >= 3) a.classification = "Stop / avoid";
  else if (useful >= 3 && bad === 0) a.classification = Number(a.effort) <= 2 ? "Hedging action" : "Robust action";
  else if (useful >= 2 && bad <= 1) a.classification = "Contingent action";
  else if (bad >= 1 || useful === 1) a.classification = "Fragile action";
  else if (neutral >= 3) a.classification = "Hedging action";
  else a.classification = "Unclassified";
}

function stressViability(result) {
  const raw = Number(result.fitScore || 0) + Number(result.strategicValue || 0) + Number(result.reversibility || 0) + Number(result.confidence || 0) - Number(result.riskScore || 0) - Number(result.workloadBurden || 0);
  return Math.max(1, Math.min(5, Math.round(((raw + 6) / 24) * 4 + 1)));
}

function stressResultLabel(result) {
  const viability = stressViability(result);
  if (result.riskScore >= 4 && result.strategicValue >= 4) return "High risk";
  if (viability >= 4) return "Strong fit";
  if (viability >= 3) return "Useful but adapt";
  if (viability >= 2) return "Unclear";
  if (result.fitScore <= 2 && result.riskScore >= 4) return "Poor fit";
  return "Fragile";
}

function updateStressTestClassification(test) {
  const labels = test.scenarioResults.map(r => r.resultLabel);
  const strongOrUseful = labels.filter(l => l === "Strong fit" || l === "Useful but adapt").length;
  const highRisk = test.scenarioResults.filter(r => r.resultLabel === "High risk" || r.riskScore >= 4).length;
  const poor = labels.filter(l => l === "Poor fit" || l === "Fragile").length;
  const avgValue = average(test.scenarioResults.map(r => r.strategicValue));
  const avgRisk = average(test.scenarioResults.map(r => r.riskScore));
  const avgReversibility = average(test.scenarioResults.map(r => r.reversibility));
  const avgConfidence = average(test.scenarioResults.map(r => r.confidence));
  let suggested = "Monitor only";
  if (poor >= 3 || highRisk >= 3 && strongOrUseful <= 1) suggested = "Stop or avoid";
  else if (strongOrUseful >= 3 && highRisk <= 1) suggested = "Robust";
  else if (avgValue >= 4 && avgRisk >= 4) suggested = "High upside / high risk";
  else if (strongOrUseful >= 1 && strongOrUseful <= 2 && poor >= 1) suggested = "Contingent";
  else if (avgReversibility >= 4 && avgConfidence >= 2.5) suggested = "Worth piloting";
  else if (poor >= 2) suggested = "Fragile";
  test.suggestedClassification = suggested;
  if (!test.overallClassification || stressClassifications.includes(test.overallClassification) === false) test.overallClassification = suggested;
  test.decisionRecommendation ||= recommendationForClassification(test.overallClassification);
  return test;
}

function recommendationForClassification(classification) {
  return ({
    "Robust": "Proceed now",
    "Contingent": "Proceed with adaptation",
    "Fragile": "Hold and monitor",
    "High upside / high risk": "Pilot first",
    "Worth piloting": "Pilot first",
    "Monitor only": "Hold and monitor",
    "Stop or avoid": "Do not proceed",
  })[classification] || "Hold and monitor";
}

function average(values) {
  const nums = values.map(Number).filter(n => Number.isFinite(n));
  return nums.length ? nums.reduce((a, b) => a + b, 0) / nums.length : 0;
}

function signalStrengthValue(strength) {
  return ({ "Not visible": 0, "Faint": 1, "Emerging": 2, "Strong": 3, "Critical": 4 })[strength] ?? 0;
}

function signalConfidenceWeight(confidence) {
  return ({ Low: 0.6, Medium: 0.8, High: 1.0 })[confidence] ?? 0.8;
}

function signalDirectionModifier(direction) {
  return ({ Increasing: 0.2, Stable: 0, Decreasing: -0.2, Unknown: 0 })[direction] ?? 0;
}

function scenarioActivation(scenarioId) {
  const linked = state.weakSignals.filter(sig => sig.linkedScenarioIds.includes(scenarioId));
  if (!linked.length) return { scenarioId, activationScore: 0, label: "Dormant", signalCount: 0, criticalSignalCount: 0, emergingOrAboveCount: 0, confidenceSummary: "No signals", topSignals: [], strongestSignal: null, recent: "" };
  const weighted = linked.map(sig => Math.max(0, signalStrengthValue(sig.currentStrength) + signalDirectionModifier(sig.direction)) * signalConfidenceWeight(sig.confidence));
  const score = Math.round((average(weighted) / 4.2) * 100);
  const criticalSignalCount = linked.filter(sig => sig.currentStrength === "Critical").length;
  const emergingOrAboveCount = linked.filter(sig => signalStrengthValue(sig.currentStrength) >= 2).length;
  const topSignals = [...linked].sort((a, b) => signalStrengthValue(b.currentStrength) - signalStrengthValue(a.currentStrength)).slice(0, 3);
  const recent = [...linked].sort((a, b) => String(b.lastReviewed).localeCompare(String(a.lastReviewed)))[0]?.lastReviewed || "";
  return {
    scenarioId,
    activationScore: Math.max(0, Math.min(100, score)),
    label: activationLabel(score),
    signalCount: linked.length,
    criticalSignalCount,
    emergingOrAboveCount,
    confidenceSummary: `${linked.filter(s => s.confidence === "High").length} high-confidence signals`,
    topSignals,
    strongestSignal: topSignals[0],
    recent,
  };
}

function activationLabel(score) {
  if (score <= 20) return "Dormant";
  if (score <= 40) return "Faint";
  if (score <= 60) return "Emerging";
  if (score <= 80) return "Active";
  return "Highly active";
}

function nextReviewDate(start, cadence) {
  const date = start ? new Date(start) : new Date();
  const days = ({ Weekly: 7, Fortnightly: 14, Monthly: 30, Quarterly: 90, "Ad hoc": 0 })[cadence] ?? 30;
  if (!days) return "";
  date.setDate(date.getDate() + days);
  return date.toISOString().slice(0, 10);
}

function importScenarioSignals(targetState) {
  const existing = new Set(targetState.weakSignals.map(sig => `${sig.title}|${sig.linkedScenarioIds.join(",")}`));
  let added = 0;
  targetState.scenarios.forEach(sc => {
    const candidates = [
      sc.fields.signs,
      ...sc.events.map(event => event.signal).filter(Boolean),
    ].filter(Boolean);
    candidates.forEach(text => {
      text.split(/\n|;/).map(v => v.trim()).filter(Boolean).forEach(line => {
        const key = `${line}|${sc.id}`;
        if (existing.has(key)) return;
        const sig = makeWeakSignal(line, [sc.id]);
        sig.category = "Service demand";
        sig.description = `Imported from ${sc.name}.`;
        sig.evidence = line;
        targetState.weakSignals.unshift(sig);
        existing.add(key);
        added += 1;
      });
    });
  });
  if (targetState.weakSignals[0]) targetState.ui.activeSignalId = targetState.weakSignals[0].id;
  logDecision(targetState, added ? `Imported ${added} early warning indicators into the weak signals monitor.` : "Checked scenario early warning indicators; no new signals to import.");
}

function downloadJson() {
  const blob = new Blob([JSON.stringify(state, null, 2)], { type: "application/json" });
  const a = document.createElement("a");
  a.href = URL.createObjectURL(blob);
  a.download = `${(state.setup.title || "scenario-studio").toLowerCase().replace(/[^a-z0-9]+/g, "-")}.json`;
  a.click();
  URL.revokeObjectURL(a.href);
}

function importJson() {
  const input = document.createElement("input");
  input.type = "file";
  input.accept = "application/json";
  input.onchange = () => {
    const file = input.files[0];
    const reader = new FileReader();
    reader.onload = () => {
      try {
        const imported = JSON.parse(reader.result);
        if (!imported || typeof imported !== "object" || !imported.setup) throw new Error("Missing workshop setup.");
        setState(s => Object.assign(s, migrateState(imported)));
        saveToast("Imported workshop data.");
      } catch (error) {
        alert(`Import failed: ${error.message}`);
      }
    };
    reader.readAsText(file);
  };
  input.click();
}

function summaryText() {
  return `${state.setup.title}\n\nFocal question: ${selectedQuestion()?.text || ""}\n\nScenarios:\n${state.scenarios.map(s => `- ${s.name}: ${s.descriptor}`).join("\n")}\n\nActions:\n${state.actions.map(a => `- ${a.title}: ${a.classification}`).join("\n")}`;
}

function matrixText() {
  return state.scenarios.map(s => `${s.name}: ${s.descriptor}`).join("\n");
}

function actionsText() {
  return ["Action\tClassification\tOwner\tTimeframe\tEffort\tConfidence\tNext decision\tDescription"].concat(state.actions.map(a => `${a.title}\t${a.classification}\t${a.owner || ""}\t${a.timeframe || ""}\t${a.effort}\t${a.confidence}\t${a.nextDecision || ""}\t${a.description}`)).join("\n");
}

async function copyText(text) {
  await navigator.clipboard.writeText(text);
  saveToast("Copied to clipboard.");
}

function saveToast(text) {
  saveState();
  const toast = document.createElement("div");
  toast.className = "badge green";
  toast.textContent = text;
  toast.style.cssText = "position:fixed;right:24px;bottom:24px;z-index:99;box-shadow:var(--shadow);";
  document.body.appendChild(toast);
  setTimeout(() => toast.remove(), 1800);
}

function startTimer() {
  clearInterval(timerHandle);
  timerHandle = setInterval(() => {
    timerSeconds = Math.max(0, timerSeconds - 1);
    const el = $("#timer");
    if (el) el.textContent = formatTime(timerSeconds);
    if (timerSeconds === 0) clearInterval(timerHandle);
  }, 1000);
}

function resetTimer() {
  clearInterval(timerHandle);
  timerSeconds = 20 * 60;
  render();
}

function formatTime(seconds) {
  const m = String(Math.floor(seconds / 60)).padStart(2, "0");
  const s = String(seconds % 60).padStart(2, "0");
  return `${m}:${s}`;
}

render();
