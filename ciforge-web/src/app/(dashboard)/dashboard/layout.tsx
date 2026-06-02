import { redirect } from "next/navigation";
import { auth } from "@/auth";
import { Sidebar } from "@/components/dashboard/sidebar";
import { DashboardHeader } from "@/components/dashboard/header";

export default async function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const session = await auth();
  if (!session) redirect("/login");

  return (
    <div className="min-h-screen flex bg-bg">
      <Sidebar user={session.user} />
      <div className="flex-1 flex flex-col ml-[240px]">
        <DashboardHeader user={session.user} />
        <main className="flex-1 p-7">{children}</main>
      </div>
    </div>
  );
}
