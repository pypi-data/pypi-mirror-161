import { NgModule } from "@angular/core";
import { CommonModule } from "@angular/common";
import { DashboardComponent } from "./dashboard.component";
import { DashboardStatsComponent } from "./dashboard-stats/dashboard-stats.component";

@NgModule({
    imports: [CommonModule],
    declarations: [DashboardComponent, DashboardStatsComponent],
})
export class DashboardModule {}
