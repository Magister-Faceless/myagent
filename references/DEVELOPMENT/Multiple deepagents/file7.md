# src/app/layout.tsx

@@ -19,7 +19,7 @@ export default function RootLayout({
}) {
  return (
    <html lang="en">
      <body className={inter.className}>
      <body className={inter.className} suppressHydrationWarning>
        <AuthProvider>
          <NuqsAdapter>{children}</NuqsAdapter>
          <Toaster position="top-right" />