# WarThunder Sights Manager
[Русская версия здесь / Russian version here](./README.md)

This program was created to make it easier to store a large number of custom sights. Due to the game's loading mechanics, having a huge number of sights (I have 3600+ pcs.) causes severe FPS drops in the sight selection menu. This program acts as a bridge: all your sights are stored inside the application, and only the ones you select will be copied into the game directory.

### Installation Instructions:

1. Download the latest version of the program from the link: [https://github.com.](https://github.com/ReDegenerator/WarThunder-Sights-Manager/releases.)
2. Download the `.exe` file, create a separate folder for it, and move the file there before the first launch. After running the program, this folder will store user files (sights, sight previews, group files, program config, and cache).
3. Now, inside the program, you can select the path to the game's sight folder. Currently (as of 2026-08-29), the path is: `C:\Users\[username]\Documents\My Games\WarThunder\Saves\ [many digits] \production\UserSights\all_tanks` (Be sure to select **all_tanks**).

### Sight Installation Instructions:

1. If you select the game's sight folder and there are already installed sights inside, they will automatically be transferred to the program (if there are too many of them, the program might freeze for a short moment).
2. You can also drag and drop a sight (`.blk` file) directly onto the program window. It will copy it to its repository, regardless of the quantity. It also works with **.zip** archives; right after downloading a sight from WTLive (where zip files are always used), you can drag them into the program without unpacking. You can drop multiple `.zip` files at once.

# Program Structure

### Repository (Sight List)

This section displays absolutely all the sights currently stored in the program's repository.

<img width="1366" height="793" alt="image" src="https://github.com/user-attachments/assets/d6943ef2-f32a-4360-8c16-94f49433f9e8" />


### Section Structure (Repository):

1. On the left is the sight display field (status, name, preview availability). You can select multiple sights at once using the following combinations: `Shift + LMB` (area selection) or `Ctrl + LMB` (point selection). **Multiple selection works in all sight lists throughout the program.**
2. On the right is the sight preview field. It displays previews for all selected sights simultaneously and can be scrolled. Hovering the cursor over it opens a window with a full view of the sight without any cropping to the bounding box. **The right field is present in many sections and has the same functionality everywhere.** <img width="1366" height="793" alt="image" src="https://github.com/user-attachments/assets/0eb01f89-9975-4cda-b9d5-d9550a8d0a7f" />
3. The "Select all" and "Clear selected" buttons are responsible for selecting all sights in the list and canceling any current selection.
4. The "Delete selected" and "Activate selected" buttons handle deleting the chosen objects and activating them, respectively (activation means copying the sight file into the game folder).
5. "Rebuild preview image" regenerates preview images for the selected sights.
6. "Refresh sights list" rescans files in the program repository. This is only needed if you manually added files via File Explorer.
7. The "Hide sights from group" toggle disables the display of sights that are already assigned to groups.

### Activated

Displays exclusively activated sights and is designed for quick access only to the sights currently in use. If a sight is located here, it means it has been copied to the game and should be marked with its corresponding status (displayed as a green circle).

<img width="1366" height="793" alt="image" src="https://github.com/user-attachments/assets/be6d1d35-d4f2-4e61-8022-8d05b3978548" />

### Section Structure (Activated):

1. Activated sight list display field on the left.
2. The "Deactivate selected" and "Delete" buttons deactivate (turn off) or delete the selected sights.
3. The "Select all" and "Clear selected" buttons are responsible for selecting all sights in the list and canceling any current selection.

### Settings

A section for configuring the program's operations. Currently, it only includes the game's sight folder path selection, but the functionality will expand in the future.

<img width="1366" height="793" alt="image" src="https://github.com/user-attachments/assets/fc191d91-1cd1-4b66-925e-430191daa208" />

# Rendering Issues

The program has some known issues with rendering previews and full-sized sight images, which fall into two categories:

1. The program cannot properly render the image due to differences in the structure of `.blk` files. Currently, most creators design sights using the editor [WTDSights](https://dimas70800.github.io/WTDSight/), and the program reads them correctly, so this is not a severe issue. However, you may occasionally find sights with a structure like this <img width="1399" height="94" alt="image" src="https://github.com/user-attachments/assets/ab764aea-8cab-4ddf-803b-d1bc2fad93c1" /> in which case the resulting image will look like this <img width="1366" height="793" alt="image" src="https://github.com/user-attachments/assets/c497e7e8-61b0-4475-a306-6bd420f7797c" />
2. Sometimes the program loses coordinates and draws certain lines that stretch beyond the display borders <img width="1366" height="793" alt="image" src="https://github.com/user-attachments/assets/1c49ef68-247e-40b1-8f0c-dc3e16382f44" /> I will do my best to fix this in future updates.
