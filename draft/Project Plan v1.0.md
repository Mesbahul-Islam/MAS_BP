# *Freight Safe*

# Project Plan (Projektisuunnitelma)

Version history (Versiohistoria)

| Version | Date | Description | Done by |
| :---- | :---- | :---- | :---- |
| 0.0 | 12.02.2026 | Applying the Project Plan template version 0.6 of the Degree Programme | Mesbahul Islam, Auri Pykäläinen, Janne Ojala, Leo Kaskela, Aloukik Aurora |

Table of Contents (Sisältö)

[**1 Project Overview and Targets (Projektin lähtökohdat ja tavoitteet)	3**](#1-project-overview-and-targets-\(projektin-lähtökohdat-ja-tavoitteet\))

[1.1 Assignment and Purpose (Toimeksianto ja tarkoitus)	3](#1.1-assignment-and-purpose-\(toimeksianto-ja-tarkoitus\))

[1.2 Results and Delivery (Tulokset ja niiden toimitus)	7](#1.2-results-and-delivery-\(tulokset-ja-niiden-toimitus\))

[1.3 Dates of Deliveries and Result Reviews (Toimitusaikataulu ja tuloskatselmoinnit)	7](#1.3-dates-of-deliveries-and-result-reviews-\(toimitusaikataulu-ja-tuloskatselmoinnit\))

[1.4 Acceptance of Delivery and Project Reviews (Tulosten hyväksyntä ja projektin katselmoinnit)	8](#1.4-acceptance-of-delivery-and-project-reviews-\(tulosten-hyväksyntä-ja-projektin-katselmoinnit\))

[1.5 Quality Targets (Laatutavoitteet)	8](#1.5-quality-targets-\(laatutavoitteet\))

[1.6 Project Success Criteria (Projektin onnistumisen kriteerit)	9](#1.6-project-success-criteria-\(projektin-onnistumisen-kriteerit\))

**2 Project Phase Plan and Schedule (Vaihesuunnitelma ja aikataulu)	9**

**3 Project Tasks (Projektin tehtävät)	11**

**4 Project Resources and Workload (Projektin resurssit ja työmäärä)	13**

[Workload Breakdown	13](#workload-breakdown)

[Weekly Resource Utilization, Overruns, and Justifications	14](#weekly-resource-utilization,-overruns,-and-justifications)

**5 Project Facilities	15**

[**5.1 Working Premises	15**](#5.1-working-premises)

[5.2 Hardware and Other Equipments (Laitteet ja muut työvälineet)	16](#5.2-hardware-and-other-equipments-\(laitteet-ja-muut-työvälineet\))

[5.3 Software (Ohjelmistot)	16](#5.3-software-\(ohjelmistot\))

**6 Project Stakeholders and Organisation (Projektin sidosryhmät ja organisaatio	16**

[6.1 Stakeholders (Sidosryhmät)	17](#6.1-stakeholders-\(sidosryhmät\))

[6.2 Steering Group (SG) (Johtoryhmä (JORY))	17](#6.2-steering-group-\(sg\)-\(johtoryhmä-\(jory\)\))

[6.3 Project Group (PG) (Projektiryhmä (PR))	18](#6.3-project-group-\(pg\)-\(projektiryhmä-\(pr\)\))

[**7 Communication Plan (Viestintäsuunnitelma)	19**](#7-communication-plan-\(viestintäsuunnitelma\))

[7.1 Contact Information (Yhteystiedot)	19](#7.1-contact-information-\(yhteystiedot\))

[7.2 Formal Reports (Viralliset raportit sidosryhmille)	19](#7.2-formal-reports-\(viralliset-raportit-sidosryhmille\))

[7.3 Internal Reporting and Communication (Projektiryhmän sisäinen raportointi ja viestintä)	20](#7.3-internal-reporting-and-communication-\(projektiryhmän-sisäinen-raportointi-ja-viestintä\))

[7.4 Meetings (Kokoukset ja palaverit)	20](#7.4-meetings-\(kokoukset-ja-palaverit\))

[7.4.1 SG Meetings (JORY kokoukset)	20](#7.4.1-sg-meetings-\(jory-kokoukset\))

[7.4.2 Other Regular Meetings (Muut säännölliset kokoukset ja palaverit)	21](#7.4.2-other-regular-meetings-\(muut-säännölliset-kokoukset-ja-palaverit\))

[**8 Important Standards and Practices (Noudatettavat standardit ja käytänteet)	21**](#8-important-standards-and-practices-\(noudatettavat-standardit-ja-käytänteet\))

[**9 Risk Management (Riskien hallinta)	22**](#9-risk-management-\(riskien-hallinta\))

[**10 The Use of AI (Tekoälyn käyttö)	23**](#10-the-use-of-ai-\(tekoälyn-käyttö\))

[10.1. AI used for the Plan (Tekoälyn käyttö projektisuunnitelman laadinnassa)	23](#10.1.-ai-used-for-the-plan-\(tekoälyn-käyttö-projektisuunnitelman-laadinnassa\))

[10.2. The Role of AI in the Project (Tekoälyn rooli projektissa)	23](#10.2.-the-role-of-ai-in-the-project-\(tekoälyn-rooli-projektissa\))

[**Appendices	24**](#appendices)

# 1 Project Overview and Targets (Projektin lähtökohdat ja tavoitteet) {#1-project-overview-and-targets-(projektin-lähtökohdat-ja-tavoitteet)}

## 1.1 Assignment and Purpose (Toimeksianto ja tarkoitus) {#1.1-assignment-and-purpose-(toimeksianto-ja-tarkoitus)}

**Background of the project**

Long distance freight transportation is the core for the global supply chain that move high value goods across countries and continents. They are often under strict deadlines and navigate through changing environmental conditions. Freight ships and lorries transport cargo that can be damaged such as perishable foods or pharmaceuticals that need temperature control, high value electronics and luxury items. Throughout the journey, these cargo face multiple risk factors that can compromise safety. 

Current fleet monitoring services rely on simple threshold based alerts such as temperature sensors that send alerts when temperature drops below a certain level. Or if door sensors are triggered then an alert is sent. While these alerts notify operators when individual parameters exceed limits, they operate in isolation without considering the bigger context or how the multiple signals may correlate to indicate that there may be more serious issues. 

Many critical cargo anomalies only become apparent when multiple factors are analyzed together. such as:

- Route deviation combined with suspicious stop duration may indicate potential theft rather than legitimate traffic delay.  
- Temperature fluctuation combined with increased CO2 levels in a refrigerated container may suggest refrigeration unit failure rather than external weather.

- Unusual vibration patterns combined with door sensor triggers may indicate tampering rather than normal road conditions.

- Speed reduction combined with unscheduled stops and communication silence may indicate hijacking rather than mechanical issues.

When such anomalies are detected, human operators usually have to analyze the situation, decide on appropriate responses, make plans and take multiple actions across different systems \- contacting drivers, adjusting monitoring parameters, notifying stakeholders, or dispatching response teams. This process is time-consuming and makes delays.The purpose of this project is to create a proof-of-concept Multi-Agent System that demonstrates how LLM-based reasoning can automatically detect complex cargo anomalies through multi-agent coordination, reason about their severity and type, propose comprehensive action plans, and execute those plans when approved by human operators.

**Core of the project**

The core objective of the project is to design and implement a Multi-Agent System architecture that is capable of:

1. Monitoring cargo conditions using monitoring agents  
2. Detect anomalous patterns in multiple parameters  
3. Use multi agent coordination and LLM reasoning to understand complex situations  
4. Generating action plans with natural language explanations  
5. Report status and outcomes to human operators

The system consists of agents, each responsible for a specific aspect of cargo monitoring, decision-making, or action execution. The architecture is based on modularity, collaborative reasoning, and human supervised actions. A prototype is to be developed and evaluated during the course of the project and based on customer feedback, the final version is to be submitted to the customer along with necessary documentation required to operate the system.

**Purpose and Intended Use of the Project** 

The main purpose of the system is to demonstrate intelligent cargo anomaly detection with action plans provided by the system that can be executed upon order for long-distance freight operations as a proof of concept. The system shows how LLM-based multi-agent coordination can detect complex threats, reason about appropriate responses, and execute corrective actions under human supervision.

The system can be used in for example, monitoring refrigerated pharmaceutical shipments on long-haul trucks, high-value electronics in container transport, or perishable food shipments. The PoC acts as a demonstration platform to show potential for integration into Fleet Management Systems with semi-autonomous response capabilities. The system acts as a decision support and semi \- automation layer. Not a full replacement of human oversight. 

The project includes: 

1. **LLM Based Route analysis agent** \- Its primary task will be to analyze vehicle positions and movement patterns across all shipments. Uses data from vehicle agents.   
2. **LLM Based Cargo Safety agent** \- It will monitor cargo specific parameters and ensure cargo safety is maintained. Uses data from vehicle agents  
3. **Orchestrator Agent \-** The central reasoning agent that uses LLMs to receive reports from all agents and negotiate with other agents. Uses reasoning to make relations between multiple signals and complex patterns. Classify the situation and generate an action plan by using the proposals from different agents. Present the action plan to the human operator and upon approval, coordinate action execution across relevant agents.  
4. **Mesa Based Simulation Environment:** To demonstrate the system, we will simulate 3-5 freight trucks/ships on different routes with various cargo types and generate realistic data streams. Also simulate available tools and actions that the agents can execute.  
5. **Web Application \-** A dashboard that will show active shipments with real time status and present outputs and take inputs. 

Here the MESA agents are data providers. MESA agents handle the physics and represent the world state. The LLM is the decision engine. Instead of Mesa agents making choices, they should pass their state to the LLM agents. The LLM agents then return "Action Commands" which are executed back inside the Mesa simulation to update the state.

**Scope and Boundaries of the Project**

The project has a limited timeframe (March 2026 \- May 2026\) and resource constraints (213 hours per person, lack of physical environment). Considering these, the boundaries of what should be included and excluded in this project have been shown.

Included in the Project Scope 

1. Web App \- A Flask-based application with dashboard for monitoring, approving and tracking actions  
2. Implementation of all the agents mentioned  
3. Simulation of freight environment using Mesa  
4. LLM integration for reasoning and coordination \- Use of Large Language Models (Paid or Open Source)

Excluded in the Project Scope 

1. Direct integration with actual trackers, temperature sensors.  
2. Integration with enterprise-level Fleet Management Systems (FMS) or Transportation Management Systems (TMS)  
3. Actual vehicle control systems. All controls are simulated  
4. Advanced machine learning models for predictive analytics (beyond LLM-based reasoning)  
5. Real-time satellite or cellular communication infrastructure  
6. Backend or persistent data storage. 

**External Factors that should be considered**

There are several external factors that may affect the development and evaluation of the system. Considering this is a proof of concept product, there are limitations to what the product can simulate.

1. Real freight operations have significantly more complexity than can be simulated, including unpredictable traffic patterns, mechanical failures, driver behavior variations, weather impacts, and infrastructure issues that cannot be fully replicated in simulation.  
2. Sensor reliability and data quality.  
3. LLM reliability and limitations may affect system performance  
4. In real systems some actions may fail due to hardware/software issues  
5. Legal and safety constraints may limit what actions are permissible  
6. Communication delays may make time-sensitive actions ineffective

**Graphical Representation**

![][image1]

## 1.2 Results and Delivery (Tulokset ja niiden toimitus) {#1.2-results-and-delivery-(tulokset-ja-niiden-toimitus)}

| Item Number | Deliverable Description | Format / Delivery Method |
| :---- | :---- | :---- |
| **1** | **Project Plan (Draft) and Supporting Documents** | **PDF** |
| **2** | **Final Application** | **Source Code in GitHub** |
| **3** | **Project Managerial Material & Archive** | **ZIP** |
| **4** | **User Guide** | **PDF** |

## 1.3 Dates of Deliveries and Result Reviews (Toimitusaikataulu ja tuloskatselmoinnit) {#1.3-dates-of-deliveries-and-result-reviews-(toimitusaikataulu-ja-tuloskatselmoinnit)}

| Review | Result/Deliverable | Date | Participants | Issues and Practices |
| :---- | :---- | :---- | :---- | :---- |
| I | Project Plan (Draft), Executive Summary Draft and Architecture | w 9 (25th February) | Project Group, Rodrigo Ortega Casellas, Yueqiang Xu | Present Initial Concepts, project scope and architecture. Agree on project priorities for development. (1.5h) |
| II | Simulation Environment and Design Prototype | w 12 | Project Group | During Sprint II, review before the final meeting (1h)\*.. |
| III | Final Application | w 19, Beginning of May (TBD) | Project Group, Rodrigo Ortega Casellas, Yueqiang Xu | Demonstrate working PoC that meets requirements agreed previously. Present evaluation results against KPIs. Test reports, simulation reports and final source code are delivered. |
| IV | Project Managerial Material & Archive | w 19 | Project Group, Rodrigo Ortega Casellas, Yueqiang Xu | All project plan documents are to be given for review and acceptance and finally, closing of the project |
| V | User Guide | w 19 | Project Group, Yueqiang Xu | Alongside the final App, the User Guide is delivered to support the user experience. Ensure clarity of usage instructions, demo video, and instructions for the system operators |

\*Materials for all these reviews will be send 3 days before the review through email.

## 1.4 Acceptance of Delivery and Project Reviews (Tulosten hyväksyntä ja projektin katselmoinnit) {#1.4-acceptance-of-delivery-and-project-reviews-(tulosten-hyväksyntä-ja-projektin-katselmoinnit)}

| Review | Date | Acceptance |
| :---- | :---- | :---- |
| I | w 9 | 1st version of the Project Plan based on the review results. Client provides feedback on the approach and novelty of the proposed plan |
| II | w 19 (TBD) | Complete working PoC approved with all final documentation |

## 1.5 Quality Targets (Laatutavoitteet) {#1.5-quality-targets-(laatutavoitteet)}

**Targets related to Results**

| Result | Quality Target | Measurement |
| :---- | :---- | :---- |
| Project Plan  | Detailed documentation about the purpose, concept, architecture, justification, resource plan, schedule and risk management | Project plan approved by the client |
| Final Application as MVP | Working application with all functionalities performing as expected. Agents working as intended with minimal hallucinations User Interface with a good UI  | Client approves of the application functionalities.  No critical bug remain and less than 3 minor bugs during final testing phase |
| Detection Accuracy | 80% simulated anomalies are detected correctly | The percentage of simulated anomalies correctly identified by the Multi-Agent System (MAS). |
| Reasoning Time | Within acceptable range | The average time taken for the Orchestrator Agent to generate a plan after an anomaly is detected |
| Plan Quality Score |  | A 1 to 5 rating provided by human operators during testing to evaluate the relevance and safety of the LLM generated action plans |

**Targets related to the Process**

| Quality Target | Measurement |
| :---- | :---- |
| Within the limits of the project resources | Resources (workload) will not exceed more than \+/- 20h of the planned total for each project member. |
| Within the schedule | For the schedule the maximum delay is 5 working days. |
| Risks are identified and mitigation plans documented and followed.  | At least 80% of the identified risks have been addressed or have mitigation actions |
| All team members attend at least 90% of scheduled project meetings.   | Attendance tracked via meeting notes; absences documented.   |

## 1.6 Project Success Criteria (Projektin onnistumisen kriteerit) {#1.6-project-success-criteria-(projektin-onnistumisen-kriteerit)}

| Success | Measurement |
| :---- | :---- |
| Acceptable (ok) | MVP delivered with all core functionalities. Project documentation is approved |
| Good | MVP includes minor additional features beyond the minimum requirements. The simulation is realistic. Has a visually pleasing UI and good UX. Documentation is clear and professional. Feedback from SG is usually positive |
| Excellent | The application is fully functional, visually polished, and has realistic simulations. All deliverables submitted ahead of schedule. Client expresses high satisfaction and potential for long-term use or further development.  |

# 2 Project Phase Plan and Schedule (Vaihesuunnitelma ja aikataulu)

*The project will follow a somewhat modified SCRUM \- based development approach for a Proof-of-Concept (PoC) software project with a short timeline (February 2026 \- May 2026\) of approximately 13 weeks. A modified version of SCRUM will be used due to the fact that daily standups and weekly or bi-weekly sprint plannings may be slightly changed to better fit the members of the group and add to progress of the project. A Waterfall model would not be suitable because the system has multiple interacting components that have to be developed simultaneously and tested with each other continuously. Therefore, the project will use short, fixed sprints where design, implementation, integration and testing are performed in parallel while maintaining the deadlines and milestones set for SG reviews.  The project will be divided into 4 sprints (2 sprints of 3 weeks each, 1 Sprint with 4 weeks and 1 Sprint with 2 weeks) and the final week will be used for project closing tasks. After each spring there will be reviews within the team to make sure the project is on track. At the end, the final review and submission will summarize the project and its results.*

*Communication will be done through Discord for daily updates and there will be weekly meetings on Discord or at the University (1h) for sprint planning, progress review and task allocation.*

The project phases are specified in the following table:

| Phase | Description | Deliverables & Decisions | Milestone |
| :---- | :---- | :---- | :---- |
| Sprint I | Project start and requirement clarification  | Draft Project Plan, Initial System Design, Technology stack selection (Flask, Mesa, LLM APIs). Approval of project scope, architecture, and prototype feature set. | 1st SG |
| Sprint II | Simulation and prototype development | Working simulation environment and initial core agent communications. Decision on confirmation of MVP features and continuation of the project within the team |  |
| Sprint III | System Development and Integration | Prototype that works seamlessly with all components of the system. Core Functionalities working properly with initial documentation. | Prototype Review |
| Sprint IV | Testing and accepting | Final MVP Application, User Guide,, Demo Video/Steps with proper documentation. Decision: Acceptance of PoC  | Final SG |
| End | Closing | All defined closing tasks done and project declared officially closed | Project Closing |

# 3 Project Tasks (Projektin tehtävät)

**Project Management**

Project management encompasses the continuous tasks that support the entire project lifecycle, including planning, coordination, monitoring, and leadership. Its purpose is to ensure that the project progresses according to objective, risks are managed accordingly, and all the stakeholders remain informed and aligned throughout the process.  

1. **Project Planning**

   Project planning covers the key targets, results, schedule, tasks, risks and their management, as well as the definition of standards and practices essential to the project. The targets are compiled into a project plan, which is deployed as a deliverable.

2.  **User Guide** 

   User guide covers the creation of all user-support materials, including the written manual, demo video, and phased usage instructions, to support the user experience of the system.

3. **Reviews**

   Reviews cover all tasks related to arrangements, organization, and documentation associated with project reviews. Review-focused tasks ensure the smoothness of deliverables and their alignment with expectations. 

4.  **Project Meetings**

   Project meetings include tasks associated with the participant gatherings, such as their planning, organizing, execution, and documentation. The meetings establish a mutual understanding of the project’s state and the current tasks related to it. 

**Testing**

Testing includes all tasks associated with testing, such as defining criteria, determining simulation test scenarios, configuring the simulation environment, and conducting actual simulation testing. The purpose of these tasks is to maintain and support the system’s functionality and correctness, as well as to ensure the preservation of quality.

1. **Quality Criteria (functional and UX)**

   Quality criteria specifies the quality expected from the system in terms of functionality and usability. The areas of correctness, performance, consistency, navigability, and informativeness are areas of interest.

2. **Simulation Test Scenarios**

   Simulation test scenario creation defines the conditions and sequences of events to be executed in a simulation environment in relation to quality criteria. The task Includes both normal and exceptional scenarios. The scenarios are documented.

3. **Simulation Environment Testing**

   Simulation environment testing covers the integration of the simulation environment and the initialization of its components. In the operational environment, the created scenarios are eventually executed. A report is compiled from the test runs.

4. **Final Evaluation**

   Technical validation confirms that the MVP meets all criteria and requirements regarding the system’s performance. 

**Development**

The development encompasses the implementation of the prototype and the MVP. The objective is to carry the plan to the execution level, that is, to deliver functioning versions of the product.

**1\. Creating the simulation environment and data streams**

Mesa-based simulation environment that represents freight trucks operating on different routes with various cargo types. Simulated sensor data streams (e.g., temperature, location, vibration, CO₂ levels, door status, speed) will be generated to mimic real cargo monitoring conditions. 

**2\. MAS Development and Integration**

This task focuses on implementing the core agents of the system such as Vehicle Monitoring Agents, Route Analysis Agent, Cargo Safety Agent, and the Orchestrator Agent. Each agent will have a defined role in monitoring. LLM integration will be used for contextual reasoning, anomaly classification, and generating natural language explanations and action plans based on inputs from the different agents.

**3\. Web Application Development**

This task includes the development of a Flask-based web dashboard that shows the active shipments, system status, detected anomalies, and proposed action plans. The interface will be used for human operators to review decisions, approve or reject actions, and track outcomes. 

**UI Design**

UI design encompasses all tasks related to the design and implementation of the system interface, taking into account structural, visual, and interactive dimensions. The aim is to create an interface solution that is intuitive and easy to navigate. 

**1\. Structure Design**

Structure designing covers the design of wireframes and the layout of elements on the base. The mutual arrangement and dynamics of the elements are illustrated, observed, and implemented. 

**2\. Visual Design**

Visual design encompasses the definition and adjustment of cosmetic attributes for elements, such as shades, sizes, densities, and shapes. A visual mockup is being developed.

**3\. Interaction Design** 

Interaction design covers a user-interactive perspective on interface development, where functional interface solutions are examined and implemented from the user’s point of view. The user interface is validated as functional when it is not only aesthetically sufficient but also usable. 

# 4 Project Resources and Workload (Projektin resurssit ja työmäärä)

This report shows the resource allocation and workload distribution to create the MAS system. Estimation is done from the assumed work hours per project phase, such as project management, designing, coding, and testing. Please refer to **Appendix 1** for detailed information

### **Workload Breakdown** {#workload-breakdown}

Each member is allocated 213 hours, resulting in a total workload of 1065 hours for the whole team. The division of work is aligned with the project timeline and the nature of the PoC system development.

The overall task distribution is as follows:

* Project Management (Project planning, project meetings, reviews, SG meetings, user guide): 374 hours

* Design (Structure design, visual design, interaction design): 152 hours

* MAS Development and Integration: 150 hours

* Simulation and Data: 41 hours

* Web Application Development: 136 hours

* Quality Criteria and Evaluation: 105 hours

* Simulation Test Scenarios and Environment Testing: 68 hours

* Final Evaluation: 38 hours

This distribution reflects the technical emphasis of the project, where the main workload is concentrated on MAS development and web application development during the middle sprints.

### **Weekly Resource Utilization, Overruns, and Justifications** {#weekly-resource-utilization,-overruns,-and-justifications}

The workload distribution follows the timeline shown in the project schedule image, where tasks are aligned with specific sprints and milestones.

**Weeks 7–8 (Sprint I – Project Start, Planning Overload):**  
These weeks focus heavily on project planning, structure design, and defining the simulation and MAS architecture. Project planning, initial reviews, and preparation for the first SG meeting require higher management involvement. Structure design and interaction design also have more hours to establish the system architecture, dashboard structure, and agent communication model. 

**Week 9 (SG Meeting and Transition to Development):**  
This week includes the SG meeting and transition from planning to development. Workload is concentrated on reviews, refinement of structure design, and preparation for simulation and MAS development. The workload slightly increases due to coordination, documentation updates, and alignment with feedback received during the SG review.

**Weeks 10–12 (Sprint II – Prototype and Simulation Development Overload):**  
During these weeks, the main workload shifts to Simulation and Data, MAS Development and Integration, and development of simulation scenarios. Developers and technical members have much higher workload due to the creation of the Mesa-based simulation environment, vehicle agents, and initial LLM integration. Project meetings continue actively to monitor progress. Overruns are justified because building the simulation environment and core MAS framework is critical for enabling later integration and testing.

**Weeks 12–14 (Sprint III – MAS and Web Application Development Overload):**  
These weeks represent the peak development phase where MAS development and Web Application Development occur simultaneously, as shown in the schedule. Interaction design and visual design are also refined to support the dashboard and human-in-the-loop interface. The workload is high due to parallel development of agents, orchestrator logic, and dashboard features. Additional hours are required for integration of simulation outputs into the web interface and continuous internal reviews to ensure system compatibility.

**Week 15 (Testing Initiation):**  
Testing activities begin alongside ongoing development. Simulation test scenarios and quality criteria definition become more prominent. The workload increases for developers and testers due to debugging, validation of anomaly scenarios (e.g., route deviation, temperature failure), and integration fixes. This transition phase justifies moderate overruns as both development and testing tasks overlap.

**Week 16 (Sprint IV – Final Application and Review Overload):**  
This week focuses on the final application, reviews, and system stabilization. Simulation environment testing and quality validation require additional effort to ensure the PoC works reliably. The workload is higher due to final debugging, refinement of MAS reasoning outputs, and preparation for acceptance.

**Weeks 17–18 (Testing and Acceptance Overload):**  
These weeks are heavily focused on simulation environment testing, quality criteria validation, and final evaluation. The team invests extra hours in testing different cargo anomaly scenarios, usability improvements, and performance validation of the multi-agent coordination. The designer and developers collaborate closely to refine the dashboard and user interaction. Overruns are justified because comprehensive testing is essential to demonstrate a realistic and functional PoC system.

**Week 19 (Closing and Submission – Finalizing Work Overload for All Roles):**  
The final week includes submission of the application, final reviews, SG meeting, user guide completion, and final evaluation. All team members contribute additional hours to documentation, final fixes, and demonstration preparation. The workload peak is justified as this phase includes final quality assurance, completion of the user guide, and ensuring that all deliverables meet the project acceptance criteria.

Overall, the workload distribution aligns with the sprint-based timeline shown in the schedule, where planning dominates early weeks, development and integration peak in the middle (Weeks 10–15), and testing, evaluation, and documentation require more effort in the final weeks (Weeks 16–19).

# 5 Project Facilities 

# 5.1 Working Premises {#5.1-working-premises}

All the working premises of the project together with the purpose for each.

| Premise | Purpose |
| :---- | :---- |
| TS134 A | For meetings between the project members only |
| Room \* 5 | Development of the project |

## 5.2 Hardware and Other Equipments (Laitteet ja muut työvälineet) {#5.2-hardware-and-other-equipments-(laitteet-ja-muut-työvälineet)}

All the hardware and other equipments of the project together with the purpose for each. Name also the stakeholder providing these facilities.

| Hardware/equipment | Purpose | Stakeholder |
| :---- | :---- | :---- |
| Server  | Hosting the system | University of Oulu |
| PC \* 5 | Project development | University of Oulu |

## 5.3 Software (Ohjelmistot) {#5.3-software-(ohjelmistot)}

All the software available for the project together with the purpose for each. Name also the owner of the licence(s). 

| Software | Purpose | Licence |
| :---- | :---- | :---- |
| VSCode | Development | Open Source |
| LangChain | MAS Framework | Open Source |
| Git | Version control | Open source |
| Mesa | Simulation Environment | Open Source |
| **Software** | **Purpose** | **Licence** |
| Discord | Communication within PG | Cloud Service, free |
| Google Drive | Documentation | Cloud Service, free |

# 6 Project Stakeholders and Organisation (Projektin sidosryhmät ja organisaatio

This chapter describes the stakeholders involvement in this project , their roles , responsibilities , and expectations , also the structure used to manage and execute the project. Clear definition of stakeholders and project organization is important to make sure effective communication , decision making ,and accountability throughout the project lifecycle.

This project follows a standard structure recommended by the degree programme in information processing science and consists of the Steering group (SG) and the project group (PG) . In addition , other supporting actors relevant to the implementation and success of the project are described as well 

## 6.1 Stakeholders (Sidosryhmät) {#6.1-stakeholders-(sidosryhmät)}

Stakeholders are individuals or organizations that have a direct or indirect interest in the project and its outcomes.Their expectations shape the project scope,quality targets , and acceptance criteria

| Organisation | Expectations/priorities |
| :---- | :---- |
| Client Company | The client company expects a working proof of concept that demonstrates intelligent cargo anomaly detection using a multi \-agent architecture and LLM based reasoning. The MVP should clearly show how multiple signals can be correlated , how decision are made, and how action plan are generated and executed under human supervision.The result should b suitable for demonstrations to potential investors and internal stakeholders |
| Degree Programme | The degree programme expects the project to be a realistic software engineering experience for students , supporting learning outcomes related to project management system design, artificial intelligence, teamwork, and professional documentation. |
| Logistics / Freight Operators (Representative) | Operationally realistic cargo mentoring , anomaly detection , and alert workflows that reflect real world freight operations and decision making in control centers  |
| Cargo Owners (e.g. pharmaceuticals, perishables) | Early detection of cargo safety risks and clear reasoning behind anomaly classification and transparent explanations that support informed decision making about cargo protection  |
| Fleet Operations / Control Center Personnel | clear, explainable alerts , and recommendation in taking actions , with human in the loop approval mechanisms that allow operators to review , approach or reject system-generated action plans efficiently. |

## 

## 6.2 Steering Group (SG) (Johtoryhmä (JORY)) {#6.2-steering-group-(sg)-(johtoryhmä-(jory))}

The steering group (SG) is the decision making and supervisory body of the project is made from the representative from the client organization and the degree programme.The SG provides strategic guidance and makes sure that the project progresses according to the agreed objectives,scope, and quality targets.

The responsibilities include \-

1. Examining and approving the main deliverables and the project plan

      2\.  Assessing development at significant turning points and SG sessions

      3\. Giving technical direction, viability, and relevance feedback

      4\. Formally deciding whether to accept, modify, or continue the project

      5\. Making sure that client expectations and academic standards are in line

| Name | Organisation | Role (and expertise) |
| :---- | :---- | :---- |
| Yueqiang Xu | Client Company | The client of the project.Expert on software business.Client in SCRUM. |
| Rodrigo Ortega Casellas | Degree Programme | The supervisor of the group,university lecturer, expert on project management and UX evaluation |

Project manager (PM) is the secretary of the SG. Project team members will be present during the SG meeting for learning. 

## 6.3 Project Group (PG) (Projektiryhmä (PR)) {#6.3-project-group-(pg)-(projektiryhmä-(pr))}

| Name | Role and responsibilities (and expertise) |
| :---- | :---- |
| Mesbahul Islam | Project manager (PM) & Scrum Master |
| Auri Pykäläinen | Team member responsible for Graphical Design and UX Testing |
| Leo Kaskela | Team member responsible for Programming (pair programming and testing followed) |
| Janne Ojala | Team member responsible for Programming (pair programming and testing followed) |
| Aloukik Arora | Team member responsible for Testing (pair programming and testing followed) |

.

# 7 Communication Plan (Viestintäsuunnitelma) {#7-communication-plan-(viestintäsuunnitelma)}

## 7.1 Contact Information (Yhteystiedot) {#7.1-contact-information-(yhteystiedot)}

Here are the contact information of the members of the Steering Group and Project Group: 

| Name | Role | E-mail, mobile, skype, etc. |
| :---- | :---- | :---- |
| Yueqiang Xu | SG Member, Product Owner | [Yueqiang.Xu@oulu.fi](mailto:Yueqiang.Xu@oulu.fi) |
| Rodrigo Ortega Casellas | SG Member, Supervisor | [Rodrigo.OrtegaCasellas@oulu.fi](mailto:Rodrigo.OrtegaCasellas@oulu.fi) |
| Mesbahul Islam | Project Manager | [Mesbahul.Islam@student.oulu.fi](mailto:Mesbahul.Islam@student.oulu.fi) |
| Janne Ojala | PG Member   | [Janne.H.Ojala@student.oulu.fi](mailto:Janne.H.Ojala@student.oulu.fi) |
| Auri Pykäläinen | PG Member | [Auri.Pykalainen@student.oulu.fi](mailto:Auri.Pykalainen@student.oulu.fi) |
| Leo Kaskela | PG Member, Secretary  | [Leo.Kaskela@student.oulu.fi](mailto:Leo.Kaskela@student.oulu.fi) |
| Aloukik Arora | PG Member   | [Aloukik.Arora@student.oulu.fi](mailto:Aloukik.Arora@student.oulu.fi) |

## 7.2 Formal Reports (Viralliset raportit sidosryhmille) {#7.2-formal-reports-(viralliset-raportit-sidosryhmille)}

Here are the formal reports to be shared with the SG. The reports will be shared before the specified SG meeting and the summary will be presented during the meeting. 

| Report | Stakeholder & Timing | Delivery |
| :---- | :---- | :---- |
| Project Plan | SG I | PDF, email |
| Final Report | SG II | PDF, email |

## 7.3 Internal Reporting and Communication (Projektiryhmän sisäinen raportointi ja viestintä) {#7.3-internal-reporting-and-communication-(projektiryhmän-sisäinen-raportointi-ja-viestintä)}

| What | Who & When | How |
| :---- | :---- | :---- |
| Weekly hours used | PM, all PG members weekly | Resource Usage in spreadsheet |
| Status of tasks and development | PM, all PG members weekly | Communication on Discord and during weekly meetings. Status of development on shared Kanban Board |

## 7.4 Meetings (Kokoukset ja palaverit) {#7.4-meetings-(kokoukset-ja-palaverit)}

### 7.4.1 SG Meetings (JORY kokoukset) {#7.4.1-sg-meetings-(jory-kokoukset)}

During the meeting, SG will decide about the future of the project based on the results till date. Project members will participate in these SG meetings for learning purposes.  

In the first SG meeting, when the suggested project plan made by the project team is reviewed, the SG will make sure the project is implementable and has a chance to survive, and that the project is planned to do what was required by the client. In the meeting, the project plan is accepted, or accepted with changes, and the decision to start the project is made. 

In the final SG meeting, the final report prepared by the project team will be reviewed. The results of the project are also reviewed. Finally, the final report may be accepted (possibly again with some modifications), and the closing tasks of the project are discussed specifically regarding project delivery and acceptance. 

| Meeting | Timing | How |
| :---- | :---- | :---- |
| SG I | February 25, 2026; 10:00 to 11:30 | Microsoft teams |
| SG II | w 19 (TBD) | Microsoft teams or in-person |

**All material to the SG meeting will be delivered 2-3 days before the meeting**.

### 7.4.2 Other Regular Meetings (Muut säännölliset kokoukset ja palaverit) {#7.4.2-other-regular-meetings-(muut-säännölliset-kokoukset-ja-palaverit)}

Other than the SG meeting, here is a list of the other meetings pertinent for this project: 

.

| Meeting | Timing | How |
| :---- | :---- | :---- |
| Sprint Planning | w 11, 16, 19 | Online meeting on Microsoft Teams/Discord |
| Daily Scrum | every day | Discord at 17:00 |

# 8 Important Standards and Practices (Noudatettavat standardit ja käytänteet) {#8-important-standards-and-practices-(noudatettavat-standardit-ja-käytänteet)}

| Topic | Description |
| :---- | :---- |
| Project management | The manual and templates from the degree programme will be used.The project manager is responsible for schedule monitoring, risk updates, and stakeholder communication throughout the project Project meetings (end of Sprints) reviews (end of Sprints and weekly) |
| Documenting results | Project documentation is done systematically at each stage (requirements, design, testing, validation). |
| **Topic** | **Description** |
| Filing | Project materials are stored in a cloud-based folder structure  |
| Version control and management | The project’s source code is managed using Git version control. Documents are stored in Google Drive. |
| Paper copies | The final approved project report is printed and signed for client archiving (if required).Other documents are delivered in electronic format (PDF).  |
| Testing | Testing focuses on the functional correctness, performance and reliability of the system. Testing is based on: functional requirements quality requirements acceptance criteria simulation scenarios |
| Designing | The system is designed as a modular multi-agent architecture.The implementation is based on LangChain framework, which is used for agent orchestration and LLM-based reasoning |
| SCRUM | In this project the Scrum approach will be slightly modified the features requested by the client together with the priorities are kept in the **Product Backlog** (link here) **Sprint Backlogs** (link) will be prepared together with the client at the beginning of each sprint The **Resource Usage** template will be used (appendix 1). The client is willing to participate the **Sprints I AND IV** Project manager will book these meetings with the client as early as possible  |
| Handing over | At the end of the project, the customer will receive: Source code (Git repository) Design documentation Test reports User guide MVP system Delivery will be in electronic format (ZIP archive or repository access). |

# 9 Risk Management (Riskien hallinta) {#9-risk-management-(riskien-hallinta)}

**Please see appendix 2 for Risk Management Plan**


# 10 The Use of AI (Tekoälyn käyttö) {#10-the-use-of-ai-(tekoälyn-käyttö)}

## 10.1. AI used for the Plan (Tekoälyn käyttö projektisuunnitelman laadinnassa) {#10.1.-ai-used-for-the-plan-(tekoälyn-käyttö-projektisuunnitelman-laadinnassa)}

 

AI tools were used in a supportive and limited manner during the preparation of this project plan, primarily to refine, structure, and improve the clarity of the written text. The core project idea, system concept, architecture, task definitions, and planning decisions are original and based on the project requirements, course guidelines, client discussions, and supporting background reports related to freight monitoring systems and multi-agent architectures. AI was mainly utilized for:

* Structuring written sections of the project plan  
* Improving academic tone and readability  
* Organizing workload descriptions and phase explanations  
* Refining wording for consistency and clarity  
* Formatting workload breakdowns and scheduling descriptions

Importantly, AI was not used to generate the project concept, technical design, or planning decisions independently. All planning elements such as project scope, task allocation, sprint structure, milestones, resource estimates, and risk considerations were defined by the project team based on the specific requirements of this PoC multi-agent cargo monitoring system. The team remains fully responsible for the content, feasibility, and accuracy of the plan.

## 10.2. The Role of AI in the Project (Tekoälyn rooli projektissa) {#10.2.-the-role-of-ai-in-the-project-(tekoälyn-rooli-projektissa)}

Our project explicitly involves the development and use of generative AI as a core component of the solution. The system is designed to leverage generative AI for defined functionalities that support the project objectives, rather than using AI only as an auxiliary planning tool. All development tools, frameworks, and libraries used in the implementation will be open source, in accordance with both transparency goals and client requirements. This ensures better auditability, flexibility, and compliance with licensing and intellectual property considerations.

From a copyright and licensing perspective, particular care is taken due to the involvement of AI and open source technologies. All generated outputs are reviewed, validated, and refined by the development team to ensure originality, correctness, and compliance with copyright requirements. Although AI can assist in generating ideas, code structures, and documentation drafts, the final deliverables are authored, verified, and owned by the project team before being transferred to the client. 

# Appendices {#appendices}

1. Resource Usage  
2. Risk Management  
3. Schedule   
4. Task List

[image1]: <data:image/png;base64,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tPIpWpkULQC6StHKp2hlUrQA6CpFK5+ilUnRAqCrFK18ilYmRQuArlK08ilamRQtALpK0cqnaGVStADoKkUrn6KVSdECoKsUrXyKViZFC4CuUrTyKVqZFC0AukrRyqdoZVK0AOgqRSufopVJ0QKgqxStfIpWJkULgK5StPIpWpkULQC6StHKp2hlUrQA6CpFK5+ilUnRAqCrFK18ilYmRQuArlK08ilamRQtALpK0cqnaGVStADoKkUrn6KVSdECoKsUrXyKViZFC4CuUrTyKVqZFC0AukrRyqdoZVK0AOgqRSufopVJ0QKgqxStfIpWJkULgK5StPIpWpkULQC6StHKp2hlUrQA6CpFK5+ilUnRAqCrFK18ilYmRQuArlK08ilamRQtALpK0cqnaGVStADoKkUrn6KVSdECoKsUrXyKViZFC4CuUrTyKVqZFC0AukrRyqdoZVK0AOgqRSufopVJ0QKgqxStfIpWJkULgK5StPIpWpkULQC6StHKp2hlUrQA6CpFK5+ilUnRAqCrFK18ilYmRQuArlK08ilamRQtALpK0cqnaGVStADoKkUrn6KVSdECoKsUrXyKViZFC4CuUrTyKVqZFC0AukrRyqdoZVK0AOgqRSufopVJ0QKgqxStfIpWJkULgK5StPIpWpkULQC6StHKp2hlUrQA6CpFK5+ilUnRAqCrFK18ilYmRQuArlK08ilamRQtALpK0cqnaGVStADoKkUrn6KVSdECoKsUrXyKViZFC4CuUrTyKVqZFC0AukrRyqdoZVK0AOgqRSufopVJ0QKgqxStfIpWJkULgK5StPIpWpkULQC6StHKp2hlUrQA6CpFK5+ilUnRAqCrFK18ilYmRQuArlK08ilamRQtALpK0cqnaGVStADoKkUrn6KVSdECoKsUrXyKViZFC4CuUrTyKVqZFC0AukrRyqdoZVK0AOgqRSufopVJ0QKgqxStfIpWJkULgK5StPIpWpkULQC6StHKp2hlUrQA6CpFK5+ilUnRAqCrFK18ilYmRQuArlK08ilamRQtALpK0cqnaGVStADoKkUrn6KVSdECoKsUrXyK1kK48sor01577ZWuuOKKomjFZfw8NmZxAjDaYl1WruOiaJXruFj3MXOawUJaeumli3+MW2yxRXG55JJLpt122616NwAYKXPmzBlfx2277bbj6zgWjqK1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9S4PXGHiY6KIxNaquG859vuTJ79emXie667slbQoWf+8OKW//6635SpuL4tWFKob/5XSlRfMT7VofXL7lE48cPJrvOn+Kd11Z+/xUaRCbDH7wym92/dftjc21WvEY4/aZf5zfXrHu19P0Vo0qe46jC1SsZXmwKNvTp85tVcgVtntunTr7akoLu85vlegjvnxrZO2aJVbdiLlrsEycz9783ghicTuyLiMwvKCw3q7B8uidfOtd6UNXtkrVtWiFSUwylEcWxU/r/ji64rL2Lr0hZ/2nr8sWqvN6b2H2OK10/t7r1Emtqrt84lewYvnjN2Ej33DjUWZirHYoheiaL3oQ737RTZ8de99KFoA81VXfG1MlKmzvjhxLHahfe6Fva1XsbXnmN3mF62ycOy3WO+28jFRtKIcxVagciwKS//z3nJ9r8CVP5/8rpTOPCql225O6eANemPVovXlfXtbnuJ6PPawLScWrdi9GVvb4jis/teKHD93/vuOnHNiSh947Pz39fZ1e5/TVK8R1496wfzHKlqLONWiFYmS8ZCX946Hil1rcQzSV0+/rThW6Vd/vKMoMdfccNd40Xrfib3LuF8UtXj8E94y8VilX1x8e3rhB+cXljkf6V2fqmjFFq849ipKTryHuK3/YPhjf3Lr+C68x7z2hvSIebfF1rgjv/ffYqwsWqfOKz4PeMn1xe7DPY6Y/9orvOi6YgvY6n1lMIpjbPWK3ZbPevdNxXOFeA9xvFhsPYvnKbfyKVoA81VXfG1MHAAfxyDF8Uexm+yU96V07eUpffWVKV30o94utigxUVLi/mXhiJx6aG9X3NEvmr/rMI6tihIWRS22hvW/Vmw9O+MzKb1xtZTe9bDebsI41iu2NsVxUbF78Kb/6923LFpvWbN3PFYcfB/FLLaYRdGK9xm3R1mK46xii1T1d4vXi/dR/nzsnN7zxK7KeK2fHdn7nMrX+MAW818j7q9oyYTEcVzVsUWRKGtH/+jWYgteHKfV9uI00wDUpbri61rKLT9xkHn89WL19mElimDsPqyOT5VXL5XSL47uXf/080arOM00itYiTGwx+1rf1qRFndjS9rPf3Z6++5vbir+QrN4+ygGoS3XF17Vc8J3ebsbYclS9bViJv2yMLWJzl55823SJLVuXn5PS777bO+i/entXomgtwsSuyx+f360tTcMKQF2qKz5Z9Indnse9dPK4KFrSkgDUpbriExlmFC1pRQDqUl3xiQwzipa0IgB1qa74RIYZRUtaEYC6VFd8IsOMoiWtCEBdqis+kWFG0ZJWBKAu1RWfyDCjaEkrAlCX6opPZJhRtKQVAahLdcUnMswoWtKKANSluuITGWYULWlFAOpSXfGJDDOKlrQiAHWprvhEhhlFS1oRgLpUV3wiw4yiJa0IQF2qKz6RYUbRklYEoC7VFZ/IMKNoSSsCUJfqik9kmFG0pBUBqEt1xScyzCha0ooA1KW64hMZZhQtaUUA6lJd8YkMM4qWtCIAdamu+ESGGUVLWhGAulRXfCLDjKIlrQhAXaorPpFhRtGSVgSgLtUVn8gwo2hJKwJQl+qKT2SYUbSkFQGoS3XFJzLMKFrSigDUpbriExlmFC1pRQDqUl3xiQwzipa0IgB1qa74RIYZRUtaEYC6VFd8IsOMoiWtCEBdqis+kWFG0ZJWBKAu1RWfyDCjaEkrAlCX6opPZJhRtKQVAahLdcUnMswoWtKKANSluuITGWYULWlFAOpSXfGJDDOKlrQiAHWprvhEhhlFS1oRgLpUV3wiw4yiJa0IQF2qKz6RYUbRklYEoC7VFZ/IMKNoSSsCUJfqik9kmFG0pBUBqEt1xScyzMwvWiINBqAusaKTnPx6ijGZScaq/yhZcFdcccW8pjpWXAJAl1x00UVpySWXTP/+97+rNzEDilaGuXPnptmzZ6f99tuvehMAjLS99947LbXUUumAAw6o3sQMKFoLqdyaVcZWLQC64k9/+lOaNWtWsX5bYokl0lVXXVW9CwtI0VpIZcEq/yEqWwB0wWWXXZYWX3zxYr12r3vdq7hcbLHFqndjASlaCyn2W8c/vsc85jHj/xjnzJlTvRsAjJQ999xzfB232WabFVu0Yh3HwlG0FsKVV16Zdt1112IL1kEHHVRc7rbbbsU/SgAYZbEuK9dxb3nLW9I111xTHIt8ySWXVO/KAtAMMkXRAoAuev3rX18dYoYUrUyKFgBddeCBB1aHmCFFK5OiBUBXvfrVr64OMUOKViZFC4CuMk9kPkUrk6IFQFftu+++1SFmSNHKpGgB0FV77bVXdYgZUrQyKVoAdJX5IfMpWpkULQC6avfdd68OMUOKViZFC4Cu2mWXXapDzJCilUnRAqCrdt555+oQM6RoZVK0AOiqHXfcsTrEDClamRQtALpq++23rw4xQ4pWJkULgK565jOfWR1ihhStTIoWAF213XbbVYeYIUUrk6IFQFdts8021SFmSNHKpGgB0FVPfOITq0PMkKKVSdECoKse97jHVYeYIUUrk6IFQFdtscUW1SFmSNHKpGgB0FWbbrppdYgZUrQyKVoAdNUmm2xSHWKGFK1MihYAXfXwhz+8OsQMKVqZFC0AumrDDTesDjFDilYmRQuArlp//fWrQ8yQopVJ0QKgq9Zdd93qEDOkaGVStADoqrXXXrs6xAwpWpkULQC6as0116wOMUOKViZFC4CuWm211apDzJCilUnRAqCrVl111eoQM6RoZVK0AOiqVVZZpTrEDClamRQtALpqueWWqw4xQ4pWJkULgK6aPXt2dYgZUrQyKVoAdNXSSy9dHWKGFK1MihYAXbX44otXh5ghRSuTogVAV42NqQm5LMFMihYAXbXEEkukO+64ozrMDChamRQtALoqjtG65ZZbqsPMgKKVSdECoKvirw5vuumm6jAzoGhlUrQA6Krll18+XX/99dVhZkDRyvTud7+7OgQAnbDiiiuma6+9tjrMDChamd773vdWhwCgExStfIpWpkMOOaQ6BACdoGjlU7QyHXbYYdUhAOgERSufopXp8MMPrw4BQCcoWvkUrUxHHHFEdQgAOkHRyqdoZTryyCOrQwDQCYpWPkUr0yc+8YnqEAB0gqKVT9HK9JnPfKY6BACdoGjlU7QyHXXUUdUhAOgERSufopXpmGOOqQ4BQCcoWvkUrUzHHXdcdQgAOkHRyqdoZfrSl75UHQKATlC08ilamb7yla9UhwCgExStfIpWphNOOKE6BACdoGjlU7Qyff3rX68OAUAnKFr5FK1MJ510UnUIADpB0cqnaGX67ne/Wx0CgE5QtPIpWplOPvnk6hAAdIKilU/RynTKKadUhwCgExStfIpWph/96EfVIQDoBEUrn6KV6Sc/+Ul1CAA6QdHKp2hlOu2006pDANAJilY+RSvTmWeeWR0CgE5QtPIpWpl++ctfVocAoBMUrXyKVqazzjqrOgQAnaBo5VO0Mp199tnVIQDoBEUrn6KV6dxzz60OAUAnKFr5FK1M559/fnUIADpB0cqnaGW68MILq0MA0AmKVj5FK9PFF19cHQKATlC08ilamS655JLqEAB0gqKVT9HKdOmll1aHAKATFK18ilam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>