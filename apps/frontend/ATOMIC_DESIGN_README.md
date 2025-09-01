# Atomic Design Structure

This document outlines the new component architecture following Atomic Design principles.

## 📁 Folder Structure

```
src/components/
├── atoms/              # Basic building blocks
├── molecules/          # Simple component combinations
├── organisms/          # Complex UI sections
├── templates/          # Layout templates
└── automation/         # Legacy automation components
```

## ⚛️ Atoms (Basic Building Blocks)

### RetroButton
Reusable button with retro styling
```tsx
<RetroButton variant="primary" size="md" leftIcon={<Icon />}>
  Button Text
</RetroButton>
```

### RetroCard  
Card container with retro themes
```tsx
<RetroCard variant="elevated" padding="lg">
  Card Content
</RetroCard>
```

### RetroIcon
Icon wrapper with retro styling
```tsx
<RetroIcon variant="turquoise" size="md">
  <IconName />
</RetroIcon>
```

### RetroBadge
Badge/tag component
```tsx
<RetroBadge variant="success" size="sm">
  Badge Text
</RetroBadge>
```

## 🧬 Molecules (Component Combinations)

### MetricCard
Displays metric with icon, value, and subtitle
```tsx
<MetricCard
  title="Active Tasks"
  value={42}
  subtitle="Background processes"
  icon={<IconBolt />}
  iconVariant="coral"
/>
```

### WorkerStatusCard
Shows worker status with details
```tsx
<WorkerStatusCard
  title="Market Monitor"
  icon={<IconEye />}
  status={{ text: "ACTIVE", variant: "success" }}
  statusItems={[...]}
/>
```

### ActionButtonGroup
Group of action buttons
```tsx
<ActionButtonGroup
  buttons={[
    { label: "Scan", icon: <IconEye />, onClick: handleScan },
    // ...
  ]}
  direction="vertical"
/>
```

## 🦠 Organisms (Complex Sections)

### MetricsGrid
Grid that organizes metrics in groups of 3
```tsx
<MetricsGrid metrics={metricsArray} />
```
- **Responsive:** 1 col (mobile), 2 col (tablet), 3 col (desktop)
- **Auto-grouping:** Divides metrics into groups of 3
- **Consistent spacing:** Uses standard grid gaps

### WorkersPanel
Combined workers status and quick actions
```tsx
<WorkersPanel
  workers={workersData}
  quickActions={actionButtons}
  onRefresh={handleRefresh}
/>
```
- **Layout:** 8/4 split (workers/actions)
- **Responsive:** Stacks on mobile

### PerformanceSection
Complete performance analytics display
```tsx
<PerformanceSection
  performance={performanceData}
  onViewReport={handleViewReport}
/>
```

### Sidebar
Navigation sidebar with user info
```tsx
<Sidebar
  isOpen={sidebarOpen}
  onClose={closeSidebar}
  user={userData}
  onLogout={handleLogout}
/>
```

## 📄 Templates (Layout Templates)

### AppLayout
Main application layout wrapper
```tsx
<AppLayout>
  <PageContent />
</AppLayout>
```
- **Features:** Sidebar, header, notifications, responsive
- **Navigation:** Auto-highlights current page
- **Theme:** Dark/light mode toggle

## 🎯 Usage Examples

### Refactored Automation Page
```tsx
export function AutomationRefactored() {
  // Data preparation
  const mainMetrics: MetricData[] = [...];
  const workersData: WorkerData[] = [...];
  const quickActions: ActionButton[] = [...];

  return (
    <Container size="xl" py="md">
      <Stack gap="lg">
        {/* Header */}
        <RetroCard variant="default" padding="lg">
          {/* Header content */}
        </RetroCard>

        {/* Metrics in groups of 3 */}
        <MetricsGrid metrics={mainMetrics} />

        {/* Workers + Actions */}
        <WorkersPanel
          workers={workersData}
          quickActions={quickActions}
          onRefresh={refreshStatus}
        />

        {/* Performance */}
        <PerformanceSection performance={performanceData} />
      </Stack>
    </Container>
  );
}
```

## 📱 Responsive Design

### Grid Breakpoints
- **base (mobile):** 1 column
- **sm (tablet):** 2 columns  
- **md (small desktop):** 3 columns
- **lg (large desktop):** 4 columns

### Component Behavior
- **MetricsGrid:** Auto-groups by 3, responsive columns
- **WorkersPanel:** 8/4 split on desktop, stacked on mobile
- **Sidebar:** Overlay on mobile, fixed on desktop

## 🎨 Design System Integration

### CSS Classes
All components use the existing retro CSS variables:
- `--retro-turquoise`
- `--retro-coral` 
- `--retro-gold`
- `--retro-brown`
- `--retro-cream`

### Typography
- `text-headline` - Main headings
- `text-title` - Card titles
- `text-caption` - Subtitles
- `text-profit` / `text-loss` - Financial values

### Component Classes
- `card` - Default card styling
- `card-elevated` - Elevated card styling
- `neumorph-inset` - Neumorphic inset effect
- `btn-primary`, `btn-secondary`, etc. - Button variants

## 🚀 Migration Guide

1. **Import new components:**
   ```tsx
   import { MetricsGrid, WorkersPanel } from '../components/organisms';
   import { RetroButton, RetroCard } from '../components/atoms';
   ```

2. **Replace old patterns:**
   - Manual grids → `MetricsGrid`
   - Individual cards → `MetricCard`
   - Button groups → `ActionButtonGroup`

3. **Update layouts:**
   - Use `AppLayout` template
   - Leverage responsive grid system
   - Follow 3-item grouping pattern

## 🔄 Benefits

- **Consistency:** Standardized components across app
- **Maintainability:** Single source of truth for UI patterns
- **Responsive:** Built-in responsive behavior
- **Reusability:** Components work across different pages
- **Performance:** Reduced code duplication
- **Accessibility:** Built-in ARIA labels and focus management
