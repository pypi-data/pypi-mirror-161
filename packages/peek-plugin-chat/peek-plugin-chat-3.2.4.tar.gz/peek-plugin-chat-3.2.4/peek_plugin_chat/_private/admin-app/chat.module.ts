import { CommonModule } from "@angular/common";
import { FormsModule } from "@angular/forms";
import { NgModule } from "@angular/core";
import { RouterModule, Routes } from "@angular/router";

// Import our components
import { ChatComponent } from "./chat.component";

// Define the routes for this Angular module
export const pluginRoutes: Routes = [
    {
        path: "",
        component: ChatComponent,
    },
];

// Define the module
@NgModule({
    imports: [CommonModule, RouterModule.forChild(pluginRoutes), FormsModule],
    exports: [],
    providers: [],
    declarations: [ChatComponent],
})
export class ChatModule {}
