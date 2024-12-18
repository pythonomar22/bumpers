import { SiteHeader } from "@/components/site-header"
import { CodeDisplay } from "@/components/code-display"
import { BasicUsageDisplay } from "@/components/basic-usage-display"
import { AdvancedUsageDisplay } from "@/components/advanced-usage-display"

export default function BlogPost() {
  return (
    <div className="min-h-screen bg-background">
      <SiteHeader />
      <main className="container py-24 max-w-3xl">
        <article className="prose prose-invert">
          <p className="text-sm text-muted-foreground">March 20, 2024</p>
          
          <h1 className="text-4xl font-bold mt-2 mb-8">
            bumpers: safety guardrails for AI agents
          </h1>

          <p className="text-lg text-muted-foreground/90 mb-12">
            As AI agents become more capable—iteratively reasoning, calling APIs, generating code, and producing complex outputs—the need for robust governance and safety measures is paramount. Bumpers is a system of safety guardrails designed specifically for AI agents. Bumpers intercepts and validates an agent's decisions at multiple points during its reasoning cycle, ensuring alignment, preventing unwanted behaviors, and delivering secure, reliable outcomes.
          </p>

          {/* Table of Contents */}
          <div className="mb-16">
            <h2 className="text-2xl font-bold mb-4">Table of Contents</h2>
            <ol className="list-decimal pl-5 space-y-2">
              <li><a href="#how-we-built" className="text-blue-400 hover:text-blue-300">How We Built It</a></li>
              <li><a href="#inspiration" className="text-blue-400 hover:text-blue-300">Inspiration and How We're Different</a></li>
              <li><a href="#cerebras" className="text-blue-400 hover:text-blue-300">Leveraging Cerebras' Fast Inference</a></li>
              <li><a href="#usage" className="text-blue-400 hover:text-blue-300">Usage</a></li>
              <li><a href="#roadmap" className="text-blue-400 hover:text-blue-300">Future Roadmap</a></li>
            </ol>
          </div>

          <section id="how-we-built" className="mb-20">
            <h2 className="text-3xl font-bold mb-6">1. How We Built It</h2>
            <p className="mb-4">
              Bumpers is composed of modular components designed for extensibility and performance:
            </p>
            
            <h3 className="text-xl font-semibold mb-2">Core Validation Engine (engine.py)</h3>
            <p className="mb-4">
              A pipeline that runs validators at specified validation points. Each validator implements a <code>validate(context)</code> method and returns a <code>ValidationResult</code>. If validation fails, the engine triggers interventions, such as blocking an action or requesting the agent to try again.
            </p>

            <h3 className="text-xl font-semibold mb-2">Validators and Policies (parser.py, validators/)</h3>
            <p className="mb-4">
              We define validators like <code>ActionWhitelistValidator</code> and <code>ContentFilterValidator</code>. For example:
            </p>
            
            <CodeDisplay />

            <p className="mb-4">
              Policies (in YAML) map these validators to validation points, enabling quick configuration changes without code rewrites.
            </p>

            <h3 className="text-xl font-semibold mb-2">Logging and Analysis (file_logger.py, analyzer.py)</h3>
            <p className="mb-4">
              Every validation event is logged as structured JSONL. Tools like the <code>BumpersAnalyzer</code> compute statistics on failed validations and interventions, helping developers refine their policies over time.
            </p>

            <h3 className="text-xl font-semibold mb-2">Agent Integration (react.py)</h3>
            <p className="mb-8">
              Bumpers hooks into an agent's query loop. Before the agent executes a selected action, we run <code>validation_engine.validate(ValidationPoint.PRE_ACTION, ...)</code>. If the action fails validation, we block it and prompt the agent for an alternative step. Similar checks occur before producing outputs.
            </p>
          </section>

          <section id="inspiration" className="mb-20">
            <h2 className="text-3xl font-bold mb-6">2. Inspiration and How We're Different</h2>

            <div className="my-8">
              <div className="border border-[#333] rounded-lg overflow-hidden">
                <img 
                  src="/blogpost1.png" 
                  alt="Comparison of LLM application flow with and without Guardrails" 
                  className="w-full"
                />
              </div>
              <a 
                href="https://www.guardrailsai.com/docs/" 
                target="_blank" 
                rel="noopener noreferrer" 
                className="text-sm text-muted-foreground mt-2 block text-center hover:text-blue-400 transition-colors"
              >
                Figure 1: Traditional Guardrails approach for LLM applications, showing input and output validation points
              </a>
            </div>

            <p className="mb-4">
              Bumpers was inspired by the growing community around AI safety and reliability tools. In particular, we drew inspiration from projects like <a href="https://www.guardrails.ai" className="text-blue-400 hover:text-blue-300" target="_blank" rel="noopener noreferrer">Guardrails</a>, which helped pioneer the concept of validating LLM outputs through schema enforcement, validators, and a modular, extensible framework. Guardrails made it easier for developers to integrate safety checks into their LLM prompt-response workflows, ensuring outputs stayed within defined boundaries.
            </p>

            <p className="mb-4">
              While Guardrails focuses on input/output validation for LLM calls and structured data generation, Bumpers takes the next logical step: we apply these safety checks not just at the prompt-response level, but at every stage of an AI agent's reasoning cycle. Agents, unlike single-turn prompts, are complex orchestration engines that plan actions, call tools, and maintain evolving state over multiple steps. This complexity demands a system that can:
            </p>

            <ul className="list-disc pl-6 mb-4">
              <li className="mb-2"><strong>Intercept Actions and Observations:</strong> In addition to validating final outputs, Bumpers inspects the agent's intermediate steps—like selecting which API to call or interpreting a tool's result—to ensure compliance and correctness throughout the process.</li>
              <li className="mb-2"><strong>Adapt to Agent-Specific Context:</strong> Unlike a single LLM response, an agent's chain-of-thought and actions are dynamic. Bumpers provides a flexible pipeline to apply different validators at multiple validation points (e.g., <code>PRE_ACTION</code>, <code>PRE_OUTPUT</code>), enabling a fine-grained approach to enforcing policies.</li>
              <li className="mb-2"><strong>Integrate with Fast Inference Backends:</strong> Bumpers doesn't just validate textual output. We leverage Cerebras' fast inference to run real-time, semantic drift checks or even adapt agent behavior mid-execution without slowing down the experience. This focus on low latency and performance is essential for production-grade AI applications.</li>
              <li className="mb-2"><strong>Enhanced Observability and Monitoring:</strong> While Guardrails provides core validation primitives, Bumpers offers a comprehensive monitoring layer. Our analytics, interventions logging, and alert conditions help teams not only ensure compliance but also understand long-term patterns, improve policies, and prevent recurring issues.</li>
            </ul>

            <p className="mb-8">
              In essence, Bumpers builds upon the foundational ideas in Guardrails—like modular validators, schemata, and prompt-to-validation pipelines—and extends them into the multi-step, multi-tool world of AI agents. By doing so, we deliver a holistic, real-time guardrail system that ensures reliability, safety, and alignment from the very first thought an agent has to its final answer.
            </p>
          </section>

          <section id="cerebras" className="mb-20">
            <h2 className="text-3xl font-bold mb-6">3. Leveraging Cerebras' Fast Inference</h2>
            <p className="mb-4">
              Integrating with Cerebras' inference engine supercharges Bumpers' real-time validations. Traditionally, injecting additional validation layers into an agent's loop could introduce latency. By offloading semantic checks and LLM-based reasoning validations to Cerebras' hardware-accelerated inference endpoint, we achieve:
            </p>
            <ul className="list-disc pl-6 mb-4">
              <li className="mb-2"><strong>Instantaneous Embedding Checks:</strong> The semantic drift validator uses embeddings to ensure the agent's answer doesn't stray from the user's original goal. With Cerebras' fast inference, generating embeddings and calculating similarity scores is near-instant.</li>
              <li className="mb-2"><strong>On-the-Fly Policy Enforcement:</strong> As soon as an action is proposed, Cerebras-backed LLM calls can classify or refine the response within milliseconds, preserving responsiveness even in complex multi-turn dialogues.</li>
            </ul>
            <p className="mb-8">
              For example, if Bumpers detects a high risk of semantic drift, it can immediately consult a Cerebras model to re-check the content, all without significantly delaying the agent's flow.
            </p>
          </section>

          <section id="usage" className="mb-20">
            <h2 className="text-3xl font-bold mb-6">4. Usage</h2>
            <p className="mb-4">
              Bumpers is designed to fit naturally into your agent’s existing workflow. Below are a few examples demonstrating how to set up and run Bumpers with your AI agent. We’ll use a ReAct-style agent combined with Cerebras-powered inference for lightning-fast validations.
            </p>

            <h3 className="text-xl font-semibold mb-2">Basic Integration</h3>
            <p className="mb-4">
              Start by configuring a logger, loading a policy file, and registering validators with the <code>CoreValidationEngine</code>. Then wrap your ReAct agent with the <code>GuardedReActAgent</code>:
            </p>

            <BasicUsageDisplay />

            <h3 className="text-xl font-semibold mb-2">Advanced Usage</h3>
            <p className="mb-4">
              For more advanced scenarios, you can add semantic drift validators, integrate monitoring conditions to trigger alerts if failure rates spike, and analyze logs to refine your policies. With Bumpers, you can scale from simple action checks to sophisticated multi-step oversight that ensures your agent always stays on track.
            </p>

            <AdvancedUsageDisplay />
          </section>

          <section id="roadmap" className="mb-20">
            <h2 className="text-3xl font-bold mb-6">5. Future Roadmap</h2>
            <p className="mb-4">
              Our vision is to expand Bumpers into a universal guardrails framework for all manner of agents and deployment scenarios:
            </p>

            <h3 className="text-xl font-semibold mb-2">Framework Integrations</h3>
            <p className="mb-4">
              We plan to add native support for popular agent frameworks like LangChain, ControlFlow, and future orchestrators.
            </p>

            <h3 className="text-xl font-semibold mb-2">Enhanced Semantic Oversight</h3>
            <p className="mb-4">
              Beyond just semantic drift, we’ll integrate vision-language models (VLMs) and advanced classifiers. For example, if using multimodal agents (like Google's rumored Mariner agent), Bumpers could ensure image-based reasoning steps remain compliant.
            </p>

            <h3 className="text-xl font-semibold mb-2">Dynamic Policy Adaptation</h3>
            <p className="mb-4">
              We'll incorporate adaptive policies that learn from historical logs and adjust automatically to changing requirements.
            </p>

            <h3 className="text-xl font-semibold mb-2">Broader Tooling & Ecosystem</h3>
            <p className="mb-8">
              We plan to build dashboards for real-time visualization of agent behavior, integration with CI/CD pipelines for compliance checks, and possibly a "coach" LLM that suggests policy improvements.
            </p>
          </section>
        </article>
      </main>
    </div>
  )
}
