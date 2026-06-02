import { auth } from "@/auth";
import { StatsRow } from "@/components/dashboard/stats-row";
import { PipelineList } from "@/components/dashboard/pipeline-list";
import { QuickGenerate } from "@/components/dashboard/quick-generate";
import { ActivityFeed } from "@/components/dashboard/activity-feed";
import { PipelineChart } from "@/components/dashboard/pipeline-chart";
import { LanguageBreakdown } from "@/components/dashboard/language-breakdown";

export default async function DashboardPage() {
  const session = await auth();
  const firstName = session?.user?.name?.split(" ")[0] || "there";

  const hour = new Date().getHours();
  const greeting =
    hour < 12 ? "Good morning" : hour < 18 ? "Good afternoon" : "Good evening";

  return (
    <div>
      {/* Page header */}
      <div className="flex items-start justify-between mb-7">
        <div>
          <h1
            className="text-[26px] font-bold tracking-tight mb-1"
            style={{ fontFamily: "var(--font-display)" }}
          >
            {greeting}, {firstName} 👋
          </h1>
          <p className="text-sm font-light" style={{ color: "var(--text2)" }}>
            Here&apos;s what&apos;s happening with your pipelines today.
          </p>
        </div>
        <QuickGenerate compact />
      </div>

      {/* Stats */}
      <StatsRow />

      {/* Main grid */}
      <div className="grid grid-cols-1 xl:grid-cols-[1fr_360px] gap-5 mt-5">
        {/* Left column */}
        <div className="flex flex-col gap-5">
          <PipelineChart />
          <div>
            <div className="flex items-center justify-between mb-4">
              <h2
                className="text-base font-semibold tracking-tight"
                style={{ fontFamily: "var(--font-display)" }}
              >
                Recent Pipelines
              </h2>
              <a
                href="/dashboard/pipelines"
                className="text-xs transition-colors"
                style={{ color: "var(--purple2)", fontFamily: "var(--font-mono)" }}
              >
                View all →
              </a>
            </div>
            <PipelineList limit={5} />
          </div>
        </div>

        {/* Right column */}
        <div className="flex flex-col gap-5">
          <QuickGenerate />
          <LanguageBreakdown />
          <ActivityFeed />
        </div>
      </div>
    </div>
  );
}
