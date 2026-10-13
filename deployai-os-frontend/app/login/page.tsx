"use client";

import { useRouter } from "next/navigation";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import Link from "next/link";
import { Boxes } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

const loginSchema = z.object({
  email: z.string().email("Enter a valid email address"),
  password: z.string().min(6, "Password must be at least 6 characters"),
});

type LoginForm = z.infer<typeof loginSchema>;

export default function LoginPage() {
  const router = useRouter();
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<LoginForm>({ resolver: zodResolver(loginSchema) });

  function onSubmit() {
    router.push("/dashboard");
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-zinc-50 px-4">
      <div className="w-full max-w-sm">
        <div className="mb-8 flex items-center justify-center gap-2">
          <Boxes className="h-6 w-6 text-brand-600" />
          <span className="text-lg font-semibold tracking-tight text-zinc-900">DeployAI OS</span>
        </div>

        <div className="rounded-xl border border-zinc-200 bg-white p-6">
          <h1 className="text-lg font-semibold text-zinc-900">Sign in</h1>
          <p className="mt-1 text-sm text-zinc-500">Enterprise AI deployment platform — reference implementation</p>

          <form className="mt-6 space-y-4" onSubmit={handleSubmit(onSubmit)}>
            <div>
              <Label htmlFor="email">Work email</Label>
              <Input id="email" type="email" placeholder="you@company.com" {...register("email")} />
              {errors.email && <p className="mt-1 text-xs text-red-600">{errors.email.message}</p>}
            </div>
            <div>
              <Label htmlFor="password">Password</Label>
              <Input id="password" type="password" placeholder="••••••••" {...register("password")} />
              {errors.password && <p className="mt-1 text-xs text-red-600">{errors.password.message}</p>}
            </div>
            <Button type="submit" className="w-full" disabled={isSubmitting}>
              Sign in
            </Button>
          </form>

          <div className="my-5 flex items-center gap-3">
            <div className="h-px flex-1 bg-zinc-200" />
            <span className="text-xs text-zinc-400">or</span>
            <div className="h-px flex-1 bg-zinc-200" />
          </div>

          <Button variant="outline" className="w-full" onClick={() => router.push("/dashboard")}>
            Continue as Demo Engineer
          </Button>
        </div>

        <p className="mt-6 text-center text-sm text-zinc-500">
          Don&#39;t have an account?{" "}
          <Link href="/register" className="font-medium text-brand-700 hover:underline">
            Create one
          </Link>
        </p>
      </div>
    </div>
  );
}
