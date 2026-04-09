*1.200 Transportation: Foundations and Methods, Spring 2026*

As part of the class, you are to carry out a project on a topic of your choice, related to the subject of this class. We believe that **learning from doing** is among the most fun and effective ways to learn. As such, the final project is an opportunity to reflect on the class by synthesizing the techniques taught with a specific transportation problem.

The topic is open-ended, and course staff will be available to guide the topic choice and presentation preparation as needed. We will also offer a running list of class project ideas: [**1.200 Class project ideas (Spring 2026)**](https://www.notion.so/1-200-Class-project-ideas-Spring-2026-3113aac19c848066b816efa3f851dcc5?pvs=21). Some ideas even come with project mentors. The list will be periodically updated.

**Important dates:**

- Friday 4/3 (11:59pm ET): Project proposal due
- Wednesday 5/6 & Friday 5/8: In-class presentations (this is a hard deadline, no late days permitted)
- Friday 5/8 (11:59 pm): Final reports due (this is a hard deadline, no late days permitted)

## Basic guidelines

The project entails a project proposal, a short in-class presentation, and a project report. **Class projects are short in duration (about 1 month), so please scope it appropriately.** We want to see you identify a problem of interest and a rough plan of attack (project proposal phase), and then to execute on that plan, synthesize your findings, and report back to us what you have learned and suggested next steps (project phase). We see this as an opportunity to explore an idea that you find interesting, or build some research infrastructure that may be useful to you later on. Negative results are just as valuable as positive results, and will not be penalized.

### There are two types of projects

1. **(Research project)** A research project is one that seeks to establish new knowledge in transportation-related fields. The project should also apply / use / extend topics from the class. Pick a particular problem of interest in the area of the subject, develop, analyze and implement a methodology to solve it. You may focus on the problem itself (that is, compute solutions for variants of the problem and develop some insights), or on an assessment of computational methods (try different algorithms, and compare their performance).
2. **(Reproducibility project)** Reproduce a transportation research paper. There are a few different options: a) Pick any paper of your choice, reproduce it to the best of your ability, and report on the difficulties and/or findings; b) Experiment with using Large Language Models for reproducing a set of papers of your choice; c) Identify a benchmark that is missing from the field and contribute towards it by reproducing a combination of methods, datasets, and metrics.

**Groups**: You can work alone or in a group of 2 people.

## Milestones

1. **Project proposals** are to be submitted via Gradescope.
    - The presentation topic proposal is a written proposal of 0.5-1 pages (excluding references), describing: 0) the project type, 1) the overall topic, 2) the specific transportation problem / paper(s) and why it’s important, and 3) the relation to one or more techniques introduced in this class. Include what background is relevant to help us help you, for example, some context on your research area / background. The course staff will provide feedback on the topic. However, you are encouraged to talk to us beforehand about the topic you have in mind.
2. **Short presentations** (no more than 15 min + a few minutes for questions) will take place in class (possibly an extended class session if needed). We encourage all students to attend if you can, and to celebrate together all we have learned this semester. *The final timing will be announced later, depending on the number of groups.* No late days can be accepted, unfortunately.
    - Video option: 3-5 minutes. Video will be shown in class, followed by a brief Q&A. We may ask you for permission later to upload the video online (e.g. Youtube).
    - The presentation order will be randomly determined. However, please let the course staff know ASAP if you have scheduling conflicts.
    - Your presentation slides (if any) should be made available to the teaching staff, via Canvas, by the start of your presentation session.
3. **Project reports** are to be submitted via Gradescope. No late days can be accepted, unfortunately.
    - Your main report should be **no more than 5 pages in length**, excluding references. Some key elements here (adapted according to your subject) would be problem statement, mathematical formulation (in good notation!), hypotheses, methods, results, conclusions. We value conciseness, focused writing, and crisp messages. Think of the style of *Nature* articles as an example.
    - You are free—but not expected or required—to write more, to provide explanations, show figures, or give proofs, in an appendix (10 more pages, maximum, including figures). The report should be self-contained.
    - You should describe and evaluate what you did in your project, which may not necessarily be what you hoped to do originally. **A small result described and evaluated well will earn more credit than an ambitious result where no aspect was done well.** Be specific in describing the problem you tried to solve. Explain in detail your approach, and specify any simplifications or assumptions you have taken. Also demonstrate the limitations of your approach. When doesn’t it work? Why? Include potential directions of future work. Make sure to add references to all related work you reviewed or used.

## More guidance on research projects

- If you choose to take a computational approach to your research project, you are free to use existing software and packages. Your time is better spent on modeling interesting problems and solving them, rather than a lot of coding. Likewise, you are free to use any of the code from any of the computational labs in the class.
- You do not have a ton of time for a class project. So, a typical research project would start with a problem of interest, and then simplify the problem to its essence such that you can model a basic problem to gain intuition on the problem of interest, while not spending a ton of time modeling minor details.
- Real-world data is always great to see. However, it can be messy and require substantial effort to clean up. So we encourage first prototyping your project idea with synthetic data, before moving to real-world data.
- **In short, start as simple as possible (and no simpler).** Gradually increase the complexity of the project (the modeling assumptions, the code, the data, etc.) as you gain intuition and confidence in your project idea.

## More guidance on reproducibility projects

**Background**: There might very well be a reproducibility crisis in transportation. Recent work, including our own, shows that only 3% of recent transportation papers actually share data & code, making it nearly impossible to build upon prior work and thereby slowing down research progress:

- **Measuring the State of Open Science in Transportation Using Large Language Models** ([arXiv](https://arxiv.org/abs/2601.14429), 2026)
- Revisiting reproducibility in transportation simulation studies ([ETRR](https://link.springer.com/article/10.1186/s12544-025-00718-9), 2025)

The good news is that this “crisis” is highly actionable, and you can be part of that solution. By reproducing a study, you will 1) contribute by enabling others to build upon that study, 2) gain the skills to make your future work reproducible, and 3) gain the know-how to enable others to do so too.

The goal of this project is therefore, to try to reproduce one or more transportation studies. We encourage you to chose studies that align with your thesis research or that you find interesting or important.

**General project tips**

- **Before you get started, snapshot the current state of reproducibility.** Each project will have a unique starting point based on the state of data and code availability for your particular topic. Providing an assessment of where things are at will help the instruction team understand what you are working with, as well as provide an accurate representation of the challenges of reproducibility (or lack thereof); we should and will evaluate a project differently if you are starting with no codebase vs a well-documented codebase!
    - You may run through a reproducibility checklist and skim the available artifacts before writing your project proposal. For example: Is there an available code repository? Is it clearly documented? Does it contain code for every analysis conducted in the paper? Every figure? Same deal with data.
    - This process will not catch everything. As you go along in your project, make sure to document issues. For example, a repository could be beautifully documented but fail to compile, omit a critical dataset, or fail to disclose some important model parameters.
    - Even if a paper provides code/data, you do not need to use it! We have had good luck in the past re-implementing a paper (say, in Python instead of MATLAB) but using the provided MATLAB implementation as reference.
- You may find this tutorial useful (Reproducibility in Transportation Research: A Hands-on Tutorial at ITSC 2024): https://www.rerite.org/itsc24-rr-tutorial/
- **Deliverables** include open artifacts—code and data—as well as the report.
    - Even if you are able to only partially reproduce something, making that available will enable others to build upon your work as a starting point.
- The report should detail: motivation behind reproducibility, lessons-learned, challenges, impediments, missing information, formal mistakes, and implicit assumptions.
- Video presentation options include (but are not limited to): focusing on a surprising aspect of reproducing a paper; a fast run-through of your reproduction process - in addition to some introduction on your choice of paper(s) and tools

Note: These reproducibility projects are part of [RERITE](https://www.rerite.org/)’s Student-in-the-loop (SiL) initiative, created by Dr. Michail Makridis at ETH. This initiative aims to establish a win-win-win for authors (dissemination), students (training), and the field (reliable baselines). These class projects (in 1.200) represent the second offering of the SiL initiative. We hope to infuse this kind of program more broadly into transportation engineering education around the world. **As such, please give us your feedback on the initiative!**

## Example project videos from Spring 2024

Undergraduate (1.041)

- https://youtu.be/krcnVC3NIr4?feature=shared

Graduate (1.200)

- https://youtu.be/czw382jGpxg?feature=shared
- https://youtu.be/D50tL80sTuU?feature=shared
- https://youtu.be/Ld70Qlw8Jv4?feature=shared

## General resources

As a general resource you can check for topics and references in:

- Your textbooks
- MIT Mobility Forum (Friday lecture series)
- Come talk to us!