# src/app/page.module.scss

@@ -11,6 +11,20 @@
.mainContent {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
  position: relative;
}

.agentHeader {
  padding: 12px 16px;
  border-bottom: 1px solid hsl(var(--border));
  background-color: hsl(var(--background));
  display: flex;
  align-items: center;
  justify-content: flex-end;
  min-height: 60px;
  position: sticky;
  top: 0;
  z-index: 100;
}