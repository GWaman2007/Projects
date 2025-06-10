from flask import Blueprint, render_template, current_app, send_from_directory, request
import csv
import os
import json
from werkzeug.exceptions import NotFound
from datetime import datetime

main_bp = Blueprint('main', __name__)


# Load all Pokémon data from the JSON file
with open("all_pokemon_data.json", "r") as f:
    all_pokemon = json.load(f)

# Assuming `all_pokemon` is a dictionary containing all Pokémon data with their IDs as keys

# Step 1: Group Pokémon by species_id
grouped_by_species = {}

for pokemon in all_pokemon.values():
    species_id = pokemon['species_id']
    if species_id not in grouped_by_species:
        grouped_by_species[species_id] = []
    grouped_by_species[species_id].append(pokemon)

# Step 2: Sort Pokémon by species_id and then by id within each species
sorted_pokedex = []
for species_id in sorted(grouped_by_species.keys()):
    # Sort Pokémon within each species by their id
    sorted_pokedex.extend(sorted(grouped_by_species[species_id], key=lambda x: x['id']))

# Step 3: Function to filter Pokémon by a range of IDs (for each generation)
def filter_generation(start_id, end_id):
    return [pokemon for pokemon in sorted_pokedex if start_id <= pokemon['id'] <= end_id]

# Step 4: Function to filter regional forms by searching the name field
def filter_regionals_by_name(region):
    # Find Pokémon with the region in their name
    return [pokemon for pokemon in sorted_pokedex if region in pokemon['name'].lower()]

# Step 5: Generate Pokedex for each generation
pokedex_gen1 = filter_generation(1, 151)
pokedex_gen2 = filter_generation(152, 251)
pokedex_gen3 = filter_generation(252, 386)
pokedex_gen4 = filter_generation(387, 493)
pokedex_gen5 = filter_generation(494, 649)
pokedex_gen6 = filter_generation(650, 721)
pokedex_gen7 = filter_generation(722, 809)
pokedex_gen8 = filter_generation(810, 898)
pokedex_gen9 = filter_generation(899, 1025)

# Step 6: Filter out regional forms for Gen 7 (Alola), Gen 8 (Galar), and Gen 9 (Paldea)
pokedex_gen7_alola = filter_regionals_by_name('-alola')  # Only Alola forms (search whole Pokédex for 'alola')
pokedex_gen8_galar = filter_regionals_by_name('-galar')  # Only Galar forms (search whole Pokédex for 'galar')
pokedex_gen9_paldea = filter_regionals_by_name('-paldea')# Only Paldea forms (search whole Pokédex for 'paldea')
pokedex_mega=filter_regionals_by_name('-mega')
pokedex_gmax=filter_regionals_by_name('-gmax')
pokedex_gen6_mega= [pokemon for pokemon in pokedex_mega if 650 <= pokemon['species_id'] <= 721]
pokedex_gen7_mega= [pokemon for pokemon in pokedex_mega if 722 <= pokemon['species_id'] <= 809]
pokedex_gen8_gmax= [pokemon for pokemon in pokedex_gmax if 810 <= pokemon['species_id'] <= 898]
# Step 7: Combine the filtered Pokémon with the full set for each generation
pokedex_gen6 = pokedex_gen6 + pokedex_gen6_mega  # Gen 6 full + Mega forms
pokedex_gen7 = pokedex_gen7 + pokedex_gen7_alola + pokedex_gen7_mega  # Gen 7 full + Alola + Mega forms
pokedex_gen8 = pokedex_gen8 + pokedex_gen8_galar + pokedex_gen8_gmax # Gen 8 full + Galar + Gmax forms
pokedex_gen9 = pokedex_gen9 + pokedex_gen9_paldea  # Gen 9 full + Paldea forms

# Final pokedex list (optional, if you want to include all generations together)
pokedex = all_pokemon# Full Pokédex with all generations combined
@main_bp.route('/pokedex_gen_1')
def pokedex_rby():
    """
    Render the Pokédex RBY page with sorting options for Generation 1 (Pokémon Red, Yellow & Blue).
    """
    search = request.args.get('search', '')
    sort_by = request.args.get("sort", "id")

    pokedex_list = pokedex_gen1  # Assuming it's a list

    if sort_by == "name":
        pokedex_sorted = sorted(pokedex_list, key=lambda p: p["name"])
    elif sort_by == "type":
        pokedex_sorted = sorted(pokedex_list, key=lambda p: p["types"][0])
    else:  # Default sorting by species_id
        pokedex_sorted = sorted(pokedex_list, key=lambda p: p["species_id"])

    return render_template("pokedex_RBY.html", pokedex=pokedex_sorted, search=search)


@main_bp.route('/pokedex_gen_2')
def pokedex_gsc():
    """
    Render the Pokédex GSC page with sorting options for Generation 2 (Pokémon Gold, Silver & Crystal).
    """
    search = request.args.get('search', '')
    sort_by = request.args.get("sort", "id")

    pokedex_list = pokedex_gen2  # Assuming it's a list

    if sort_by == "name":
        pokedex_sorted = sorted(pokedex_list, key=lambda p: p["name"])
    elif sort_by == "type":
        pokedex_sorted = sorted(pokedex_list, key=lambda p: p["types"][0])
    else:  # Default sorting by species_id
        pokedex_sorted = sorted(pokedex_list, key=lambda p: p["species_id"])

    return render_template("pokedex_GSC.html", pokedex=pokedex_sorted, search=search)


@main_bp.route('/pokedex_gen_3')
def pokedex_rse():
    """
    Render the Pokédex RSE page with sorting options for Generation 3 (Pokémon Ruby, Sapphire, Emerald).
    """
    search = request.args.get('search', '')
    sort_by = request.args.get("sort", "id")

    pokedex_list = pokedex_gen3  # Assuming it's a list

    if sort_by == "name":
        pokedex_sorted = sorted(pokedex_list, key=lambda p: p["name"])
    elif sort_by == "type":
        pokedex_sorted = sorted(pokedex_list, key=lambda p: p["types"][0])
    else:  # Default sorting by species_id
        pokedex_sorted = sorted(pokedex_list, key=lambda p: p["species_id"])

    return render_template("pokedex_RSE.html", pokedex=pokedex_sorted, search=search)


@main_bp.route('/pokedex_gen_4')
def pokedex_dppt():
    """
    Render the Pokédex DPPt page with sorting options for Generation 4 (Pokémon Diamond, Pearl, Platinum).
    """
    search = request.args.get('search', '')
    sort_by = request.args.get("sort", "id")

    pokedex_list = pokedex_gen4  # Assuming it's a list

    if sort_by == "name":
        pokedex_sorted = sorted(pokedex_list, key=lambda p: p["name"])
    elif sort_by == "type":
        pokedex_sorted = sorted(pokedex_list, key=lambda p: p["types"][0])
    else:  # Default sorting by species_id
        pokedex_sorted = sorted(pokedex_list, key=lambda p: p["species_id"])

    return render_template("pokedex_DPPt.html", pokedex=pokedex_sorted, search=search)


@main_bp.route('/pokedex_gen_5')
def pokedex_bw():
    """
    Render the Pokédex BW page with sorting options for Generation 5 (Pokémon Black, White).
    """
    search = request.args.get('search', '')
    sort_by = request.args.get("sort", "id")

    pokedex_list = pokedex_gen5  # Assuming it's a list

    if sort_by == "name":
        pokedex_sorted = sorted(pokedex_list, key=lambda p: p["name"])
    elif sort_by == "type":
        pokedex_sorted = sorted(pokedex_list, key=lambda p: p["types"][0])
    else:  # Default sorting by species_id
        pokedex_sorted = sorted(pokedex_list, key=lambda p: p["species_id"])

    return render_template("pokedex_BW.html", pokedex=pokedex_sorted, search=search)


@main_bp.route('/pokedex_gen_6')
def pokedex_xy():
    """
    Render the Pokédex XY page with sorting options for Generation 6 (Pokémon X, Y).
    """
    search = request.args.get('search', '')
    sort_by = request.args.get("sort", "id")

    pokedex_list = pokedex_gen6  # Assuming it's a list

    if sort_by == "name":
        pokedex_sorted = sorted(pokedex_list, key=lambda p: p["name"])
    elif sort_by == "type":
        pokedex_sorted = sorted(pokedex_list, key=lambda p: p["types"][0])
    else:  # Default sorting by species_id
        pokedex_sorted = sorted(pokedex_list, key=lambda p: p["species_id"])

    return render_template("pokedex_XY.html", pokedex=pokedex_sorted, search=search)


@main_bp.route('/pokedex_gen_7')
def pokedex_sm():
    """
    Render the Pokédex SM page with sorting options for Generation 7 (Pokémon Sun, Moon).
    """
    search = request.args.get('search', '')
    sort_by = request.args.get("sort", "id")

    pokedex_list = pokedex_gen7  # Assuming it's a list

    if sort_by == "name":
        pokedex_sorted = sorted(pokedex_list, key=lambda p: p["name"])
    elif sort_by == "type":
        pokedex_sorted = sorted(pokedex_list, key=lambda p: p["types"][0])
    else:  # Default sorting by species_id
        pokedex_sorted = sorted(pokedex_list, key=lambda p: p["species_id"])

    return render_template("pokedex_SM.html", pokedex=pokedex_sorted, search=search)


@main_bp.route('/pokedex_gen_8')
def pokedex_ss():
    """
    Render the Pokédex SS page with sorting options for Generation 8 (Pokémon Sword, Shield).
    """
    search = request.args.get('search', '')
    sort_by = request.args.get("sort", "id")

    pokedex_list = pokedex_gen8  # Assuming it's a list

    if sort_by == "name":
        pokedex_sorted = sorted(pokedex_list, key=lambda p: p["name"])
    elif sort_by == "type":
        pokedex_sorted = sorted(pokedex_list, key=lambda p: p["types"][0])
    else:  # Default sorting by species_id
        pokedex_sorted = sorted(pokedex_list, key=lambda p: p["species_id"])

    return render_template("pokedex_SS.html", pokedex=pokedex_sorted, search=search)


@main_bp.route('/pokedex_gen_9')
def pokedex_sv():
    """
    Render the Pokédex SV page with sorting options for Generation 9 (Pokémon Scarlet & Violet).
    """
    search = request.args.get('search', '')
    sort_by = request.args.get("sort", "id")

    pokedex_list = pokedex_gen9  # Assuming it's a list

    if sort_by == "name":
        pokedex_sorted = sorted(pokedex_list, key=lambda p: p["name"])
    elif sort_by == "type":
        pokedex_sorted = sorted(pokedex_list, key=lambda p: p["types"][0])
    else:  # Default sorting by species_id
        pokedex_sorted = sorted(pokedex_list, key=lambda p: p["species_id"])

    return render_template("pokedex_SV.html", pokedex=pokedex_sorted, search=search)



@main_bp.route('/pokedex_nat')
def pokedex_nat():
    """
    Render the Pokédex National page with sorting options for all Pokémon.
    """
    search = request.args.get('search', '')
    sort_by = request.args.get("sort", "id")

    pokedex_list = list(pokedex.values())

    if sort_by == "name":
        pokedex_sorted = sorted(pokedex_list, key=lambda p: p["name"])
    elif sort_by == "type":
        pokedex_sorted = sorted(pokedex_list, key=lambda p: p["types"][0])
    else:  # Default sorting by species_id
        pokedex_sorted = sorted(pokedex_list, key=lambda p: p["species_id"])

    return render_template("pokedex_nat.html", pokedex=pokedex_sorted, search=search)


@main_bp.route('/')
def home():
    """
    Render the home page with the most recent blog posts sorted by post id.

    Returns:
        Rendered home page template with up to 5 most recent posts.
    """
    posts = []
    csv_path = os.path.join(current_app.root_path, 'data', 'posts.csv')

    try:
        if os.path.exists(csv_path):
            with open(csv_path, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                posts = [row for row in reader]

                # Sort posts by id in descending order
                posts.sort(key=lambda x: int(x['id']), reverse=True)

    except (IOError, csv.Error) as e:
        current_app.logger.error(f"Error reading posts CSV: {e}")

    # Pass only the top 5 posts to the template
    return render_template("home.html", posts=posts, page_keywords="latest guides, tech tutorials, gaming insights")


@main_bp.route('/blog/<slug>')
def blog_post(slug):
    """
    Render a specific blog post by its slug.

    Args:
        slug (str): The unique slug identifier for the blog post.

    Returns:
        Rendered blog post template with post details and images, or 404 if not found.
    """
    csv_path = os.path.join(current_app.root_path, 'data', 'posts.csv')
    post = None
    post_images = []

    try:
        if os.path.exists(csv_path):
            with open(csv_path, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    if row['slug'] == slug:
                        post = row
                        break

        if not post:
            raise NotFound(f"Post with slug {slug} not found")

        # Retrieve images for the post
        image_folder = os.path.join(current_app.root_path, 'guides', post['image_folder'])

        if post.get('images'):
            # Split images from CSV and filter existing files
            post_images = [
                img for img in post['images'].split(',')
                if os.path.exists(os.path.join(image_folder, img))
            ]

        # Update view count
        update_view_count(slug)

        # Read HTML content
        html_path = os.path.join(current_app.root_path, 'guides', post['html_file'])
        with open(html_path, 'r', encoding='utf-8') as file:
            post_content = file.read()

        # Define keywords for the post
        page_keywords = post.get('keywords', '')  # Assuming keywords are stored in the CSV

        return render_template('blog_post.html',
                               post=post,
                               post_images=post_images,
                               post_content=post_content,
                               page_keywords=page_keywords)

    except NotFound:
        return render_template('errors/404.html'), 404
    except (IOError, csv.Error) as e:
        current_app.logger.error(f"Error processing blog post {slug}: {e}")
        return render_template('errors/500.html'), 500

@main_bp.route('/category/<category>')
def category(category):
    """
    Render posts for a specific category.

    Args:
        category (str): The category to filter posts by.

    Returns:
        Rendered category template with filtered posts.
    """
    posts = []
    csv_path = os.path.join(current_app.root_path, 'data', 'posts.csv')

    try:
        if os.path.exists(csv_path):
            with open(csv_path, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                posts = [
                    row for row in reader
                    if row['category'].lower() == category.lower()
                ]
                posts.sort(key=lambda x: x['date'], reverse=True)
    except (IOError, csv.Error) as e:
        current_app.logger.error(f"Error reading posts for category {category}: {e}")

    # Define keywords based on the posts in this category

    return render_template('category.html', posts=posts, category=category)

@main_bp.route('/image/<slug>/<path:filename>')
def serve_image(slug, filename):
    """
    Serve images for blog posts with enhanced security and error handling.

    Args:
        slug (str): The unique slug identifier for the blog post.
        filename (str): Name of the image file.

    Returns:
        Image file or 404 if not found.
    """
    try:
        # Define the directory for images based on the blog's slug
        directory = os.path.join(current_app.root_path, 'guides', 'images', slug)

        # Validate and sanitize filename to prevent directory traversal attacks
        safe_filename = os.path.basename(filename)

        # Serve the file from the determined directory
        return send_from_directory(directory, safe_filename)
    except FileNotFoundError:
        return render_template('errors/404.html'), 404

def update_view_count(slug):
    """
    Increment view count for a specific blog post.

    Args:
        slug (str): The unique slug identifier for the blog post.

    Raises:
        IOError: If there are issues reading or writing the CSV file.
    """
    csv_path = os.path.join(current_app.root_path, 'data', 'posts.csv')
    temp_path = os.path.join(current_app.root_path, 'data', 'temp.csv')

    try:
        if os.path.exists(csv_path):
            with open(csv_path, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                headers = reader.fieldnames
                rows = list(reader)

            with open(temp_path, 'w', newline='', encoding='utf-8') as file:
                writer = csv.DictWriter(file, fieldnames=headers)
                writer.writeheader()
                for row in rows:
                    if row['slug'] == slug:
                        row['views'] = str(int(row['views']) + 1)
                    writer.writerow(row)

            os.replace(temp_path, csv_path)
    except (IOError, csv.Error) as e:
        current_app.logger.error(f"Error updating view count for {slug}: {e}")
        # Optionally, you could add fallback logic or re-raise the exception

@main_bp.route('/sitemap.xml')
def sitemap():
    return render_template('sitemap.xml')  # Display the sitemap