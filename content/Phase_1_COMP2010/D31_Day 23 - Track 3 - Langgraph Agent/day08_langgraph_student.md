# day08 langgraph student

**File gốc:** `Phase_1_COMP2010\D31_Day 23 - Track 3 - Langgraph Agent\day08_langgraph_student.md`

---

### LangGraph & Agentic Orchestration

Day 08 · State Machines cho Agents · 2h theory + 2h guided lab
Instructor
VinUniversity · Phase2·Track3·Week5

---

### “Khi agent cần loop, retry, human

approval và resume sau crash,
chain một chiều còn đủ không?”
Giữcâuhỏinàytrongđầukhihọcbàihômnay

---

### Nội dung bài học

1. Mụctiêu&lịchhọc
2. Khinàochainkhôngđủ?
3. CoreAPI
4. Persistence&TimeTravel
5. Human-in-the-Loop&ErrorRecovery
6. Lab4giờ
7. Takeaways
Instructor (VinUni) AICB·Day08 Week5 1/25

---

### 01

Mục tiêu & lịch học
2giờlýthuyếtcôđọng,2giờlabcóhướngdẫn;bàilab
thiếtkếđủ4giờđểphânloạinănglực.

---

### Sau buổi học, học viên làm được gì?

Conceptual outcomes
■ PhânbiệtLCELchain,agentloop
vàstatefulgraph.
■ Thiếtkếstate,node,edge,
reducertrongLangGraph.
■ Hiểucheckpointing,timetravel,
HITLvàerrorrecovery.
Practical outcomes
■ Xâydựngworkflowcóconditional
routing,retryvàinterrupt.
■ Ghitrace/metricphụcvụchấm
điểm.
■ Viếtreportkỹthuậtngắntheo
rubricproduction.
Checkpoint: Cuối buổi: mỗi nhóm demo một graph chạy được trên test
casecơbản;họcviêngiỏihoànthiệnthêmcrashrecoveryvàreport.
Instructor (VinUni) AICB·Day08 Week5 2/25

---

### Timeline 4 giờ

00:00 01:00 02:00 03:00 04:00
Lý thuyết + tương tác Lab 4h: core + extension
2h lý thuyết
■ 20’LCELgap+statemachine
■ 30’StateGraphAPI
■ 25’persistence+checkpointing
■ 25’HITL+errorrecovery
■ 20’metric/reportbriefing
2h trên lớp + 2h mở rộng
■ 0-2h: buildrunnablecoregraph
■ 2-3h: persistence+crash-resume
■ 3-4h: metrics,report,polish
Instructor (VinUni) AICB·Day08 Week5 3/25

---

### 02

Khi nào chain không đủ?
LCELphùhợppipelinemộtchiều;agentproduction
thườngcầntrạngthái,nhánh,vònglặpvàkiểmsoátlỗi.

---

### LCEL Chain: con đường một chiều

Retrieve LLM Output
khó loop lại
khó pause cho human
khó resume sau crash
Chain đủ khi:
■ taskđơngiản,single-shot;
■ khôngcầnretrythôngminh;
■ khôngcầnhumanapproval;
■ khôngcầnlưustatedàihạn.
Workflowcủabạncócầnquyết
định bước tiếp theo dựa trên
kếtquảbướctrướckhông?Nếu
có,hãynghĩtớigraph.
Instructor (VinUni) AICB·Day08 Week5 4/25

---

### Production gap: 5 vấn đề thường gặp

Retrylogic Loop+con-
ditionaledge
Humanapproval interrupt+resume
Dynamicrouting conditionaledges
Crashrecovery checkpointing
Parallelwork fan-out+reducer
LCEL gap LangGraph pattern
Minipoll-4phút
Trongsảnphẩmbạntừnglàm,vấnđềnàoxuấthiệnnhiềunhất: retry,rout-
ing,humanapproval,crashrecoveryhayparallelwork?
Instructor (VinUni) AICB·Day08 Week5 5/25

---

### LangGraph trong một câu

LangGraph — Framework orchestration theo graph:typed state +
node functions + edges/conditional edges + checkpointingđểxây
workflowagentcóloop,interrupt,persistencevàfaulttolerance.
Khi dùng
■ agentcầnnhiềubướcvàquyết
địnhđộng;
■ cầnhuman-in-the-loop;
■ cầnkhôiphụcsaulỗi;
■ cầntrace/debug.
Khi chưa cần
■ promptđơnlẻ;
■ ETLtuyếntính;
■ khôngcóstate;
■ khôngcầnapprovalhoặcaudit.
docs.langchain.com/oss/python/langgraph/overview
Instructor (VinUni) AICB·Day08 Week5 6/25

---

### Ví dụ thực tế: support ticket triage

Flow
1. Nhậnticket.
2. Classify: billing,bug,policy,urgent.
3. Nếuthiếuthôngtin: hỏilạikhách.
4. Nếurủirocao: dừngđểhuman
approve.
5. Nếutoollỗi: retryhoặcdead-letter.
Routing, loop hỏi lại, HITL và
retryđềuphụthuộcstatehiện
tại. Một chain tuyến tính sẽ
nhanhtrởnênkhómaintain.
Think-pair-share-5phút
Viết 1 state field cần có cho
ticketworkflowvàlýdo.
Instructor (VinUni) AICB·Day08 Week5 7/25

---

### 03

Core API
State,node,edge,reducerlàbốnkháiniệmnềntảngcủa
StateGraph.

---

### State Machine: khái niệm cốt lõi

START plan execute done? END
yes
no: retry
State: {messages,plan,tool_results,
attempt,status,pending_approval}
Pythonfunctionđọcstatevàtrảvề
partialupdate.
Đường chuyển bước; có thể cố
địnhhoặcconditional.
Instructor (VinUni) AICB·Day08 Week5 8/25

---

### State design: code-level

from typing import Annotated, TypedDict
from operator import add
class AgentState(TypedDict):
messages: Annotated[ list[str], add]
query: str
route: str
attempt: int
tool_results: Annotated[ list[str], add]
final_answer: str | None
errors: Annotated[ list[str], add]
5 quy tắc thiết kế state
1. Flat,ítnesteddict.
2. Reducerrõcholist.
3. Typedvàvalidateđược.
4. Lean: khônglưubloblớn.
5. Versionedkhischemathay
đổi.
Lưu ý: Default reducer là
overwrite. Nếu2nodecùng
ghi một field list mà không
khaibáoreducer,rấtdễmất
dữliệu.
Instructor (VinUni) AICB·Day08 Week5 9/25

---

### Reducer: luật merge state

Overwrite phù hợp cho
■ statushiệntại;
■ routehiệntại;
■ finalanswer;
■ counternếuchỉmộtnodeghi.
Append phù hợp cho
■ messages;
■ toolresults;
■ errors;
■ auditevents;
■ metricrecords.
Quickcheck-3phút
Field audit_lognênoverwritehayappend? Vìsao?
Instructor (VinUni) AICB·Day08 Week5 10/25

---

### Node function: nguyên tắc production

def classify_node(state: AgentState) -> dict:
# TODO(student): implement routing policy
route = classify_query(state[ "query"])
return {
"route": route,
"messages": [f "classified:{route}"],
}
def tool_node(state: AgentState) -> dict:
# Nodes should be small and testable
result = run_tool(state[ "query"])
return {"tool_results": [result]}
Checklist
■ Pure-ish: khôngsideeffect
nếutránhđược.
■ Idempotentchoretry.
■ Returnpartialupdate,
khôngmutatetoànstate.
■ Logđủchoaudit.
■ Timeoutvàerrortyped.
Instructor (VinUni) AICB·Day08 Week5 11/25

---

### Conditional edges: dynamic routing

classify route
simple_qa
rag_search
full_agent
output
easy
medium
hard
Nhậnstate,trảvềtênnhánh
tiếp theo. Dùng để tối ưu
cost,latencyvàrisk.
■ Easyquery: cheappath.
■ Missinginfo: askuser.
■ Riskyaction: approval.
■ Repeatederror:
fallback/dead-letter.
Instructor (VinUni) AICB·Day08 Week5 12/25

---

### Graph wiring: từ node sang runnable graph

from langgraph.graph import StateGraph, START, END
graph = StateGraph(AgentState)
graph.add_node("classify", classify_node)
graph.add_node("answer", answer_node)
graph.add_node("tool", tool_node)
graph.add_edge(START, "classify")
graph.add_conditional_edges(
"classify", route_next,
{"simple": "answer", "tool": "tool"},
)
graph.add_edge("answer", END)
compiled = graph. compile(checkpointer=saver)
Build order
1. Definestateschema.
2. Implementnodes.
3. Implementroute
functions.
4. Addedges.
5. Compilewith
checkpointer.
6. Invokewiththreadid.
Instructor (VinUni) AICB·Day08 Week5 13/25

---

### 04

Persistence & Time T ravel
Checkpointingbiếngraphthànhworkflowcóthểpause,
resume,replayvàdebug.

---

### Checkpointing: state snapshot mỗi bước

plan
C1
execute
C2
CRASH resume output
loadcheckpoint
Memory saver:
nhanh, không bền
saurestart.
SQLite saver: persis-
tent,dễdemo.
Postgres saver: phù
hợp service nhiều
thread.
Lưu ý: Largestate=checkpointlớn=chậm. Lưureferencesthayvìfull
document/blob.
Instructor (VinUni) AICB·Day08 Week5 14/25

---

### Thread, checkpoint, time travel

■ Thread: mộtphiênworkflow,vídụmộtuserrequesthoặcmộtticket.
■ Checkpoint: snapshotstatesaumỗisuper-stepkhigraphcó
checkpointer.
■ Replay: chạylạitừmộtcheckpointđểdebughoặcA/Btestroutekhác.
■ Update state: chỉnhstatetạicheckpointtrướckhiresume,hữuíchcho
HITL.
Khikháchbáo“agentgửisaiemail”,bạncầnstatehistoryđểbiếtnodenào
quyếtđịnhsai,inputlúcđólàgì,humanđãapprovehaychưa.
docs.langchain.com/oss/python/langgraph/persistence
Instructor (VinUni) AICB·Day08 Week5 15/25

---

### Invoke với thread id

config = { "configurable": { "thread_id": "ticket-123"}}
result = compiled.invoke(
{"query": "Refund request for order 42"},
config=config,
)
snapshot = compiled.get_state(config)
history = list(compiled.get_state_history(config))
Lab metric liên quan
■ Cóthreadidriêngcho
mỗirun.
■ Cóstatehistorysaurun.
■ Cótraceeventsđủđể
tínhnodecount,retry
count,approvalcount.
Instructor (VinUni) AICB·Day08 Week5 16/25

---

### 05

Human-in-the-Loop & Error
Recovery
Agentproductionphảibiếtkhinàotựlàm,khinàohỏi
người,khinàodừngantoàn.

---

### Human-in-the-loop: interrupt và resume

draft INTERRUPT send/action END
approve
edit/reject
Approvaltrướcdestructiveaction;
clarification khi thiếu thông tin;
escalationkhivượtquyền;review
trướcpublish.
Graphpause,lưustate;humantrả
lời;graphresumetừđúngvịtrívới
statemới.
Role-play-6phút
Một bạn đóng agent, một bạn đóng reviewer. Reviewer chỉ được approve
khistatecóđủevidence.
Instructor (VinUni) AICB·Day08 Week5 17/25

---

### HITL code skeleton

from langgraph.types import interrupt, Command
def approval_node(state: AgentState) -> dict:
decision = interrupt({
"action": state[ "proposed_action"],
"risk": state[ "risk_level"],
"evidence": state[ "tool_results"],
})
return {"approval": decision}
# Resume later:
compiled.invoke(Command(resume={ "approved": True}), config)
Chấm điểm lab
■ Cóinterruptobjectrõ
ràng.
■ Córoute
approve/reject/edit.
■ Reportghisốlần
approvalvàkếtquả.
■ Khôngexecute
destructiveactionkhi
chưaapprove.
Instructor (VinUni) AICB·Day08 Week5 18/25

---

### Error recovery: retry, fallback, dead-letter

llm/toolcall error? next
fallback
dead-letter
no
retry
maxretry
fail
3 tầng
1. Retryvớibackoffvàmax
attempts.
2. Fallbackmodel/tool.
3. Dead-letterđểmanualreview.
Lưu ý: Node retry phải idem-
potent. Gửiemail,chargepay-
ment, update database cần
idempotencykey.
Instructor (VinUni) AICB·Day08 Week5 19/25

---

### Observability: trace, metric, report

Metrics bắt buộc
■ tasksuccessrate;
■ nodesvisited;
■ retrycount;
■ interruptcount;
■ statevalidationerrors;
■ latencyperrun;
■ resumesuccess.
Report bắt buộc
■ architecturediagram;
■ stateschema;
■ testcases;
■ metricstable;
■ failureanalysis;
■ improvementplan.
Checkpoint:Labsẽchấmbằngcảcodechạyđược,metricsJSONvàreport
markdown.
Instructor (VinUni) AICB·Day08 Week5 20/25

---

### 06

Lab 4 giờ
XâyLangGraphworkflowchoagentxửlýyêucầusupport
córouting,HITL,retryvàmetricreport.

---

### Lab objective

■ Hoànthiệnproductionskeletonrepo: stateschema,nodes,graphwiring,
persistenceadapter.
■ Chạy6testscenarios: simple,tool,missing-info,risky-action,
transient-error,max-error.
■ XuấtfilemetricsJSONvàreportmarkdowntheotemplate.
■ Họcviêngiỏihoànthànhextension: crash-resume,time-traveldebug
hoặcparallelfan-out.
Skeletonđãcóvùng TODO(student). Khôngcầnviếtlạikiếntrúcrepo; tập
trunghoànthiệnlogicvàbằngchứngchấmđiểm.
Instructor (VinUni) AICB·Day08 Week5 21/25

---

### Lab milestones 4 giờ

Thờigian Việccầnlàm Deliverable
0-30’ Setup repo, chạy tests baseline, đọc
stateschema
screenshot/testslog
30-75’ Implementcorenodes+graphwiring coretestspass
75-120’ Conditionalrouting+retry+HITLmock 6scenariosrun
120-180’ Persistence/checkpoint+crash-resume
extension
traceJSON/history
180-225’ Metricsrunner+reporttemplate metrics.json + re-
port.md
225-240’ Demo,cleanup,self-assessment finalzip/repo
Instructor (VinUni) AICB·Day08 Week5 22/25

---

### Scoring rubric

Hạngmục Điểm Tiêuchí
Architecture&state 20 Typed state, reducer đúng, node nhỏ và
testable
Graphbehavior 25 Routingđúng,retrycógiớihạn,HITLhoạt
động
Persistence&recovery 15 Checkpoint,threadid,resumehoặcmock
tươngđương
Metrics&tests 20 Metrics JSON hợp lệ, 6 scenarios, tests
pass
Report&demo 15 Report rõ, failure analysis, dia-
gram/screenshot
Productionhygiene 5 README,config,typing,lint,envhandling
Instructor (VinUni) AICB·Day08 Week5 23/25

---

### Demo format cuối lab

1. Graphcủabạncónhữngnodenàovàstatefieldquantrọngnhấtlàgì?
2. Mộttestcaseđiquaroutenào? Córetry/interruptkhông?
3. MetricsJSONchothấysuccessrate,retrycount,interruptcountlàbao
nhiêu?
4. Bạnđãchứngminhresume/crashrecoverythếnào?
5. Nếuthêm1ngày,bạnsẽproductionizephầnnàotrước?
Instructor (VinUni) AICB·Day08 Week5 24/25

---

### 07

T akeaways
LangGraphkhôngchỉlàthưviệnorchestration;nólàcách
thiếtkếagentnhưmộtsystemcóstate,auditvàrecovery.

---

### Tổng kết — Key T akeaways

Những ý chính cần nhớ trướckhisangbàitiếptheo
■ DùngLCELchopipelinetuyếntính;dùngLangGraphkhicóloop,
conditionalroute,persistencehoặcHITL.
■ Stateschemavàreducerquyếtđịnhđộổnđịnhcủagraph.
■ CheckpointinglànềntảngchoHITL,memory,timetravelvàfault
tolerance.
■ Productionagentcầnmetric,tracevàreport,khôngchỉdemochạyđược.
Instructor (VinUni) AICB·Day08 Week5 24/25

---

### References

1. LangGraphdocumentation: Persistence,Human-in-the-loop,FunctionalAPI.
docs.langchain.com/oss/python/langgraph
2. LangGraphreference: StateGraph,interrupt,Command,checkpointers. reference.langchain.com
3. LangChainblog/docsexamplesforagentworkflowsanddeployment. langchain.com
Instructor (VinUni) AICB·Day08 Week5 25/25