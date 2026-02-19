# Angular 20 Setup Reference

## 1. Create .nvmrc File

Create `.nvmrc` in the project root to specify Node.js version:

```
20.19
```

This ensures consistent Node.js version across development environments using nvm.

## 2. Initialize Angular Project

```bash
# Use correct Node.js version (if using nvm)
nvm use

# Create Angular project with routing and SCSS
ng new <project-name> --routing --style=scss --skip-git

# Move to src/ui location
mkdir -p src
mv <project-name> src/ui

# Navigate to UI directory
cd src/ui

# Add Angular Material
ng add @angular/material
```

## 3. Create Folder Structure

Create the following directories under `src/ui/src/app/`:

```
app/
├── core/
│   ├── interceptors/
│   │   ├── auth.interceptor.ts
│   │   └── index.ts
│   ├── services/
│   │   └── index.ts
│   ├── guards/
│   │   └── index.ts
│   └── index.ts
├── shared/
│   ├── components/
│   │   └── index.ts
│   ├── directives/
│   │   └── index.ts
│   ├── pipes/
│   │   └── index.ts
│   ├── material/
│   │   ├── material.module.ts
│   │   └── index.ts
│   ├── shared.module.ts
│   └── index.ts
└── features/
    └── (feature modules go here)
```

## 4. TypeScript Configuration

Update `src/ui/tsconfig.json` with path aliases:

```json
{
  "compileOnSave": false,
  "compilerOptions": {
    "outDir": "./dist/out-tsc",
    "strict": true,
    "noImplicitOverride": true,
    "noPropertyAccessFromIndexSignature": true,
    "noImplicitReturns": true,
    "noFallthroughCasesInSwitch": true,
    "skipLibCheck": true,
    "isolatedModules": true,
    "esModuleInterop": true,
    "sourceMap": true,
    "declaration": false,
    "experimentalDecorators": true,
    "moduleResolution": "bundler",
    "importHelpers": true,
    "target": "ES2022",
    "module": "ES2022",
    "useDefineForClassFields": false,
    "lib": ["ES2022", "dom"],
    "baseUrl": "./",
    "typeRoots": ["node_modules/@types"],
    "paths": {
      "@core/*": ["src/app/core/*"],
      "@shared/*": ["src/app/shared/*"],
      "@features/*": ["src/app/features/*"]
    }
  },
  "angularCompilerOptions": {
    "enableI18nLegacyMessageIdFormat": false,
    "strictInjectionParameters": true,
    "strictInputAccessModifiers": true,
    "strictTemplates": true
  }
}
```

## 5. HTTP Interceptor

Create `src/ui/src/app/core/interceptors/auth.interceptor.ts`:

```typescript
import { HttpInterceptorFn } from "@angular/common/http";
import { catchError, throwError } from "rxjs";

/**
 * HTTP Interceptor for API requests
 * - Adds Authorization header to API requests
 * - Handles 401 responses
 */
export const authInterceptor: HttpInterceptorFn = (req, next) => {
  // Get token from storage (implement as needed)
  const token = localStorage.getItem("auth_token");

  // Clone request and add Authorization header if token exists
  let authReq = req;
  if (token && isApiRequest(req.url)) {
    authReq = req.clone({
      setHeaders: {
        Authorization: `Bearer ${token}`,
      },
    });
  }

  // Handle the request and catch authentication errors
  return next(authReq).pipe(
    catchError((error) => {
      // Handle 401 Unauthorized responses
      if (error.status === 401 && isApiRequest(req.url)) {
        // Clear invalid auth state
        localStorage.removeItem("auth_token");
        // Redirect to login or handle as needed
        console.error("Authentication failed");
      }
      return throwError(() => error);
    })
  );
};

/**
 * Check if the request is an API request
 */
function isApiRequest(url: string): boolean {
  return url.startsWith("/api/") || url.includes("localhost");
}
```

Create `src/ui/src/app/core/interceptors/index.ts`:

```typescript
export * from "./auth.interceptor";
```

## 6. Material Module

Create `src/ui/src/app/shared/material/material.module.ts`:

```typescript
import { NgModule } from "@angular/core";

// Material Components
import { MatButtonModule } from "@angular/material/button";
import { MatIconModule } from "@angular/material/icon";
import { MatToolbarModule } from "@angular/material/toolbar";
import { MatCardModule } from "@angular/material/card";
import { MatFormFieldModule } from "@angular/material/form-field";
import { MatInputModule } from "@angular/material/input";
import { MatSelectModule } from "@angular/material/select";
import { MatCheckboxModule } from "@angular/material/checkbox";
import { MatDialogModule } from "@angular/material/dialog";
import { MatSnackBarModule } from "@angular/material/snack-bar";
import { MatProgressSpinnerModule } from "@angular/material/progress-spinner";
import { MatMenuModule } from "@angular/material/menu";
import { MatSidenavModule } from "@angular/material/sidenav";
import { MatListModule } from "@angular/material/list";
import { MatTableModule } from "@angular/material/table";
import { MatTooltipModule } from "@angular/material/tooltip";

const MATERIAL_MODULES = [
  MatButtonModule,
  MatIconModule,
  MatToolbarModule,
  MatCardModule,
  MatFormFieldModule,
  MatInputModule,
  MatSelectModule,
  MatCheckboxModule,
  MatDialogModule,
  MatSnackBarModule,
  MatProgressSpinnerModule,
  MatMenuModule,
  MatSidenavModule,
  MatListModule,
  MatTableModule,
  MatTooltipModule,
];

@NgModule({
  imports: MATERIAL_MODULES,
  exports: MATERIAL_MODULES,
})
export class MaterialModule {}
```

Create `src/ui/src/app/shared/material/index.ts`:

```typescript
export * from "./material.module";
```

## 7. Core Module

Create `src/ui/src/app/core/modules/core.module.ts`:

```typescript
import { NgModule } from "@angular/core";
import { CommonModule } from "@angular/common";
import { ReactiveFormsModule, FormsModule } from "@angular/forms";
import { RouterModule, RouterLink } from "@angular/router";
import { MarkdownModule } from "ngx-markdown";
import { FullCalendarModule } from "@fullcalendar/angular";

const CORE_MODULES = [
  // Angular Core Modules
  CommonModule,
  ReactiveFormsModule,
  FormsModule,
  RouterModule,
  RouterLink,
  MarkdownModule,
  FullCalendarModule,
];

@NgModule({
  imports: CORE_MODULES,
  exports: CORE_MODULES,
})
export class CoreModule {}
```

Create `src/ui/src/app/core/modules/index.ts`:

```typescript
export * from "./core.module";
```

**Note:** Add any commonly used third-party modules (like MarkdownModule, FullCalendarModule) to this module. Feature components can import CoreModule to get all frequently used modules at once.

## 8. Shared Module

Create `src/ui/src/app/shared/shared.module.ts`:

```typescript
import { NgModule } from "@angular/core";
import { CommonModule } from "@angular/common";
import { FormsModule, ReactiveFormsModule } from "@angular/forms";
import { MaterialModule } from "./material/material.module";

@NgModule({
  imports: [CommonModule, FormsModule, ReactiveFormsModule, MaterialModule],
  exports: [CommonModule, FormsModule, ReactiveFormsModule, MaterialModule],
})
export class SharedModule {}
```

Create `src/ui/src/app/shared/index.ts`:

```typescript
export * from "./shared.module";
export * from "./material";
export * from "./components";
export * from "./directives";
export * from "./pipes";
```

## 9. Core Index

Create `src/ui/src/app/core/index.ts`:

```typescript
export * from "./interceptors";
export * from "./services";
export * from "./guards";
```

## 10. Proxy Configuration

Create `src/ui/proxy.conf.json`:

```json
{
  "/api": {
    "target": "http://localhost:<API_PORT>",
    "secure": false,
    "changeOrigin": false,
    "logLevel": "debug",
    "ws": true
  }
}
```

Replace `<API_PORT>` with the configured API port.

## 11. Update angular.json

Add proxy configuration to serve options in `angular.json`:

```json
{
  "serve": {
    "options": {
      "proxyConfig": "proxy.conf.json"
    }
  }
}
```

## 12. App Configuration

Update `src/ui/src/app/app.config.ts` to include the interceptor:

```typescript
import { ApplicationConfig, provideZoneChangeDetection } from "@angular/core";
import { provideRouter } from "@angular/router";
import { provideHttpClient, withInterceptors } from "@angular/common/http";
import { provideAnimationsAsync } from "@angular/platform-browser/animations/async";

import { routes } from "./app.routes";
import { authInterceptor } from "@core/interceptors";

export const appConfig: ApplicationConfig = {
  providers: [
    provideZoneChangeDetection({ eventCoalescing: true }),
    provideRouter(routes),
    provideHttpClient(withInterceptors([authInterceptor])),
    provideAnimationsAsync(),
  ],
};
```
